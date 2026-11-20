#include <cstdint>
#include <cstdio>
#include <vector>
// Deterministic ARM smoke target; not a payment or wallet binary.
int main() {
    const std::vector<std::uint8_t> sample{0x00, 0x47, 0x01, 0x00};
    std::uint32_t checksum = 0;
    for (const auto byte : sample) checksum = (checksum * 257u) + byte;
    std::printf("GAMMA_ARM_CODEC_PROBE v1 bytes=%zu checksum=%u\n", sample.size(), checksum);
    return sample.size() == 4 && sample[0] == 0 ? 0 : 1;
}
