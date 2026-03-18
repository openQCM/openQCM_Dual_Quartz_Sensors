/*
  openQCM_Dual_fw versione 2.0

  Optimized firmware for dual-channel Quartz Crystal Microbalance (QCM) system.

  Changes from v1.0:
  - Non-blocking main loop: no delay() calls, frequency data is never missed
  - Atomic reading of count_output[] with interrupt guard (fixes race condition)
  - Fixed double newline in TEC "Te?" command
  - Fixed tone not stopping when diff == 0
  - Non-blocking TEC serial communication (state machine)
  - Non-blocking PC command handling
  - Replaced Arduino String with static char buffers (no heap fragmentation)
  - Removed unused MULT_FACTOR

  Hardware platform: Teensy 4.0
  Timer configuration:
  - QuadTimer4_1 (Pin 6  - B0_10, ALT1)  -> Reference
  - QuadTimer4_2 (Pin 9  - B0_11, ALT1)  -> Sensor

  Based on FreqCountMany by Paul Stoffregen (PJRC)
  https://github.com/PaulStoffregen/FreqCountMany
  https://forum.pjrc.com/threads/71193-Teensy-4-Measuring-multiple-frequencies

  version: 2.0
  date: 2026-03-16
  author: Marco Mauro (openQCM Team)
*/

#include <IntervalTimer.h>
#include "src/Adafruit_MCP9808.h"

// ============================================================================
// Configuration
// ============================================================================

// QCM Frequency Measurement
#define GATE_INTERVAL   2000    // microseconds for each gate interval
#define GATE_ACCUM      500     // number of intervals to accumulate (total = 1s)
#define OUTPUT_PIN      23      // TTL output for frequency difference
#define PWM_COOL_FAN    7       // Fan PWM control pin
#define RPM_COOL_FAN    12      // Fan RPM sense pin

// TEC Control
#define MTD415T_TIME_SEC_STARTUP  1000
#define STATUS_TEC        10
#define CTRL_SWITCH_PIN   11
#define ENABLE_PIN        8

// Timing (non-blocking loop)
#define TEMP_READ_INTERVAL_MS   1000   // how often to request temperature
#define TEC_SERIAL_TIMEOUT_MS   50     // max wait for TEC response

// Serial buffers (no dynamic String allocation)
#define CMD_BUF_SIZE  64
#define TEC_BUF_SIZE  32

// ============================================================================
// Hardware objects
// ============================================================================

Adafruit_MCP9808 tempsensor = Adafruit_MCP9808();
IntervalTimer gateTimer;

// ============================================================================
// Timer / frequency counting
// ============================================================================

typedef struct {
  IMXRT_TMR_t *timer;
  int timerchannel;
  int pin;
  int pinconfig;
  volatile uint32_t *inputselectreg;
  int inputselectval;
} timerinfo_t;

const timerinfo_t timerlist[] = {
  {&IMXRT_TMR4, 1, 6, 1, NULL, 0},   // Reference
  {&IMXRT_TMR4, 2, 9, 1, NULL, 0}    // Sensor
};

#define NUM_TIMERS (sizeof(timerlist) / sizeof(timerinfo_t))

volatile bool     count_update = false;
volatile uint32_t count_output[NUM_TIMERS];

// ============================================================================
// ISR: gate timer — runs every GATE_INTERVAL µs
// ============================================================================

static uint16_t read_count(unsigned int n) {
  static uint16_t prior[NUM_TIMERS];
  if (n >= NUM_TIMERS) return 0;
  uint16_t count = (timerlist[n].timer)->CH[timerlist[n].timerchannel].CNTR;
  uint16_t inc = count - prior[n];   // handles 16-bit wrap automatically
  prior[n] = count;
  return inc;
}

void gate_timer() {
  static unsigned int count = 0;
  static uint32_t accum[NUM_TIMERS];

  for (unsigned int i = 0; i < NUM_TIMERS; i++) {
    accum[i] += read_count(i);
  }

  if (++count >= GATE_ACCUM) {
    for (unsigned int i = 0; i < NUM_TIMERS; i++) {
      count_output[i] = accum[i];
      accum[i] = 0;
    }
    count_update = true;
    count = 0;
  }
}

// ============================================================================
// Non-blocking TEC serial communication
// ============================================================================

enum TecState {
  TEC_IDLE,
  TEC_WAIT_RESPONSE
};

static TecState   tec_state = TEC_IDLE;
static uint32_t   tec_request_time = 0;
static char       tec_buf[TEC_BUF_SIZE];
static uint8_t    tec_buf_pos = 0;

// Read a line from Serial1 into tec_buf without blocking.
// Returns true when a complete line is available.
static bool tec_read_line() {
  while (Serial1.available()) {
    char c = Serial1.read();
    if (c == '\n' || c == '\r') {
      if (tec_buf_pos > 0) {
        tec_buf[tec_buf_pos] = '\0';
        tec_buf_pos = 0;
        return true;
      }
      // skip empty lines
    } else if (tec_buf_pos < TEC_BUF_SIZE - 1) {
      tec_buf[tec_buf_pos++] = c;
    }
  }
  return false;
}

static void tec_flush() {
  while (Serial1.available()) {
    Serial1.read();
  }
}

// ============================================================================
// Non-blocking PC command handling
// ============================================================================

static char     cmd_buf[CMD_BUF_SIZE];
static uint8_t  cmd_buf_pos = 0;

// Read a line from Serial (USB) without blocking.
// Returns true when a complete command is available.
static bool pc_read_line() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (cmd_buf_pos > 0) {
        cmd_buf[cmd_buf_pos] = '\0';
        cmd_buf_pos = 0;
        return true;
      }
    } else if (cmd_buf_pos < CMD_BUF_SIZE - 1) {
      cmd_buf[cmd_buf_pos++] = c;
    }
  }
  return false;
}

// ============================================================================
// Setup
// ============================================================================

void setup() {
  Serial.begin(115200);
  Serial1.begin(115200);

  pinMode(STATUS_TEC, INPUT);
  pinMode(CTRL_SWITCH_PIN, OUTPUT);
  pinMode(ENABLE_PIN, OUTPUT);

  // MTD415T temperature control active by default
  digitalWrite(CTRL_SWITCH_PIN, LOW);
  digitalWrite(ENABLE_PIN, LOW);

  pinMode(OUTPUT_PIN, OUTPUT);
  pinMode(PWM_COOL_FAN, OUTPUT);
  pinMode(RPM_COOL_FAN, OUTPUT);

  tempsensor.begin();

  // Wait for MTD415T startup
  delay(MTD415T_TIME_SEC_STARTUP);
  tec_flush();

  // QCM Frequency Measurement: enable QuadTimer clocks
  CCM_CCGR6 |= CCM_CCGR6_QTIMER1(CCM_CCGR_ON) | CCM_CCGR6_QTIMER2(CCM_CCGR_ON)
             | CCM_CCGR6_QTIMER3(CCM_CCGR_ON) | CCM_CCGR6_QTIMER4(CCM_CCGR_ON);

  // Configure timer channels for edge counting
  for (unsigned int i = 0; i < NUM_TIMERS; i++) {
    IMXRT_TMR_t *timer = timerlist[i].timer;
    int ch = timerlist[i].timerchannel;
    timer->CH[ch].CTRL   = 0;
    timer->CH[ch].CNTR   = 0;
    timer->CH[ch].LOAD   = 0;
    timer->CH[ch].COMP1  = 65535;
    timer->CH[ch].CMPLD1 = 65535;
    timer->CH[ch].SCTRL  = 0;
    timer->CH[ch].CTRL   = TMR_CTRL_CM(1) | TMR_CTRL_PCS(ch) | TMR_CTRL_LENGTH;
    int pin = timerlist[i].pin;
    *portConfigRegister(pin) = timerlist[i].pinconfig;
    if (timerlist[i].inputselectreg) {
      *timerlist[i].inputselectreg = timerlist[i].inputselectval;
    }
  }

  // Start the gate timer ISR
  gateTimer.begin(gate_timer, GATE_INTERVAL);
}

// ============================================================================
// Main loop — fully non-blocking
// ============================================================================

void loop() {

  // ----- 1. QCM Frequency: highest priority, checked every iteration -----
  if (count_update) {
    // Atomic read: disable interrupts to prevent ISR from writing
    // between reading channel 0 and channel 1
    noInterrupts();
    uint32_t freq0 = count_output[0];
    uint32_t freq1 = count_output[1];
    count_update = false;
    interrupts();

    int32_t diff = (int32_t)freq1 - (int32_t)freq0;

    // TTL output: frequency = |diff|, stop if zero
    if (diff != 0) {
      tone(OUTPUT_PIN, (diff > 0) ? diff : -diff);
    } else {
      noTone(OUTPUT_PIN);
    }

    Serial.printf("F%u,%u,%d\n", freq0, freq1, diff);
  }

  // ----- 2. Temperature reading: periodic, non-blocking -----
  uint32_t now = millis();

  switch (tec_state) {
    case TEC_IDLE: {
      static uint32_t last_temp_request = 0;
      if (now - last_temp_request >= TEMP_READ_INTERVAL_MS) {
        last_temp_request = now;

        // Request TEC temperature (no extra \n — println adds \r\n)
        Serial1.println("Te?");
        tec_state = TEC_WAIT_RESPONSE;
        tec_request_time = now;
        tec_buf_pos = 0;

        // Read onboard MCP9808 (~5ms I2C, acceptable)
        float c = tempsensor.readTempC();
        Serial.printf("C%.3f\n", c);
      }
      break;
    }

    case TEC_WAIT_RESPONSE: {
      if (tec_read_line()) {
        // Got TEC response
        Serial.printf("T%s\n", tec_buf);
        tec_state = TEC_IDLE;
        tec_flush();  // discard any trailing data
      } else if (now - tec_request_time > TEC_SERIAL_TIMEOUT_MS) {
        // Timeout — TEC did not respond
        tec_state = TEC_IDLE;
        tec_flush();
      }
      break;
    }
  }

  // ----- 3. PC commands: non-blocking -----
  if (pc_read_line()) {
    // Forward command to MTD415T
    Serial1.println(cmd_buf);

    // Wait briefly for response (short blocking, acceptable for commands)
    uint32_t cmd_start = millis();
    while (!Serial1.available() && (millis() - cmd_start < TEC_SERIAL_TIMEOUT_MS)) {
      // Check frequency while waiting
      if (count_update) {
        noInterrupts();
        uint32_t f0 = count_output[0];
        uint32_t f1 = count_output[1];
        count_update = false;
        interrupts();
        int32_t d = (int32_t)f1 - (int32_t)f0;
        if (d != 0) tone(OUTPUT_PIN, (d > 0) ? d : -d);
        else noTone(OUTPUT_PIN);
        Serial.printf("F%u,%u,%d\n", f0, f1, d);
      }
    }

    // Read and forward response
    if (tec_read_line()) {
      Serial.println(tec_buf);
    }
    tec_flush();
  }
}
