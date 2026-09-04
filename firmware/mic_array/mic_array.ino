// 4-mic array (2x INMP441 stereo pairs) for sound direction-of-arrival tracking.
// I2S_NUM_0 reads mic pair A (front/back), I2S_NUM_1 reads mic pair B (left/right).
// Each INMP441's L/R select pin is wired directly to GND (left) or 3V3 (right) to
// pick its channel, so two mics share one I2S bus (SCK/WS/SD lines in parallel).
//
// Streams 4-channel 16-bit PCM over USB serial to the Python side
// (turion/hardware/mic_array_doa.py), which does the actual GCC-PHAT direction
// estimate. Pin numbers and channel order are placeholders -- update once the
// InMoov head is built and real mic positions are known.

#include <driver/i2s.h>

// I2S bus 0 -- mic pair A (front + back)
#define I2S0_WS   25
#define I2S0_SCK  26
#define I2S0_SD   27

// I2S bus 1 -- mic pair B (left + right)
#define I2S1_WS   32
#define I2S1_SCK  33
#define I2S1_SD   34

#define SAMPLE_RATE        8000   // voice-band is enough for direction-finding, keeps serial bandwidth low
#define SAMPLES_PER_BLOCK  256    // ~32ms per block at 8kHz
#define SERIAL_BAUD        921600

const uint32_t FRAME_MAGIC = 0x4D494334; // "MIC4", lets the Python side resync if a byte is dropped

int32_t bufA[SAMPLES_PER_BLOCK * 2]; // interleaved L/R from I2S bus 0
int32_t bufB[SAMPLES_PER_BLOCK * 2]; // interleaved L/R from I2S bus 1
int16_t outFrame[SAMPLES_PER_BLOCK * 4]; // [front, back, left, right] interleaved

void setupI2S(i2s_port_t port, int ws, int sck, int sd) {
  i2s_config_t cfg = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT, // INMP441 outputs 24-bit data left-justified in a 32-bit slot
    .channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT,
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 4,
    .dma_buf_len = SAMPLES_PER_BLOCK,
    .use_apll = false,
  };
  i2s_pin_config_t pins = {
    .bck_io_num = sck,
    .ws_io_num = ws,
    .data_out_num = I2S_PIN_NO_CHANGE,
    .data_in_num = sd,
  };
  i2s_driver_install(port, &cfg, 0, NULL);
  i2s_set_pin(port, &pins);
}

void setup() {
  Serial.begin(SERIAL_BAUD);
  setupI2S(I2S_NUM_0, I2S0_WS, I2S0_SCK, I2S0_SD);
  setupI2S(I2S_NUM_1, I2S1_WS, I2S1_SCK, I2S1_SD);
}

void loop() {
  size_t bytesReadA = 0, bytesReadB = 0;
  i2s_read(I2S_NUM_0, bufA, sizeof(bufA), &bytesReadA, portMAX_DELAY);
  i2s_read(I2S_NUM_1, bufB, sizeof(bufB), &bytesReadB, portMAX_DELAY);

  size_t framesA = bytesReadA / sizeof(int32_t) / 2;
  size_t framesB = bytesReadB / sizeof(int32_t) / 2;
  size_t frames = min(framesA, framesB);
  if (frames > SAMPLES_PER_BLOCK) frames = SAMPLES_PER_BLOCK;

  for (size_t i = 0; i < frames; i++) {
    // top 16 bits of the 24-bit sample (which itself sits in the top 24 bits of the 32-bit word)
    outFrame[i * 4 + 0] = (int16_t)(bufA[i * 2 + 0] >> 16); // front
    outFrame[i * 4 + 1] = (int16_t)(bufA[i * 2 + 1] >> 16); // back
    outFrame[i * 4 + 2] = (int16_t)(bufB[i * 2 + 0] >> 16); // left
    outFrame[i * 4 + 3] = (int16_t)(bufB[i * 2 + 1] >> 16); // right
  }

  uint16_t frameCount = (uint16_t)frames;
  Serial.write((uint8_t*)&FRAME_MAGIC, sizeof(FRAME_MAGIC));
  Serial.write((uint8_t*)&frameCount, sizeof(frameCount));
  Serial.write((uint8_t*)outFrame, frames * 4 * sizeof(int16_t));
}
