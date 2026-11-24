#include "servo/sg90_angle.hpp"

namespace module {

ServoStatus angleToPulseUs(const Sg90Calibration& cal,
                           float deg,
                           std::uint16_t& out) noexcept
{
    if (!cal.valid()) {
        return ServoStatus::InvalidArgument;
    }
    if (deg < cal.min_angle_deg || deg > cal.max_angle_deg) {
        return ServoStatus::InvalidArgument;
    }

    const float angle_span = cal.max_angle_deg - cal.min_angle_deg;
    const float pulse_span =
        static_cast<float>(cal.max_pulse_us - cal.min_pulse_us);
    const float ratio = (deg - cal.min_angle_deg) / angle_span;
    const float pulse_f = static_cast<float>(cal.min_pulse_us) + ratio * pulse_span;

    /* 四舍五入到最近的 us */
    const std::uint32_t pulse_u = static_cast<std::uint32_t>(pulse_f + 0.5f);
    if (pulse_u < cal.min_pulse_us || pulse_u > cal.max_pulse_us) {
        return ServoStatus::InvalidArgument;
    }

    out = static_cast<std::uint16_t>(pulse_u);
    return ServoStatus::Ok;
}

ServoStatus pulseUsToAngle(const Sg90Calibration& cal,
                           std::uint16_t pulse_us,
                           float& out) noexcept
{
    if (!cal.valid() ||
        pulse_us < cal.min_pulse_us ||
        pulse_us > cal.max_pulse_us) {
        return ServoStatus::InvalidArgument;
    }

    const float pulse_span =
        static_cast<float>(cal.max_pulse_us - cal.min_pulse_us);
    const float ratio = static_cast<float>(pulse_us - cal.min_pulse_us) / pulse_span;
    out = cal.min_angle_deg + ratio * (cal.max_angle_deg - cal.min_angle_deg);
    return ServoStatus::Ok;
}

} // namespace module
