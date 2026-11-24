#pragma once

#include <cstdint>

#include "interfaces/i_servo.hpp"

namespace module {

/**
 * @brief SG90 角度—脉宽标定
 *
 * 默认按常见 SG90 给 500..2500us 对应 0..180°。
 * 实际舵机可能有偏差，建议用 setPulseUs 实测后修改：
 *   0° 对应多少 us、180° 对应多少 us。
 */
struct Sg90Calibration {
    float min_angle_deg{0.0f};
    float max_angle_deg{180.0f};
    std::uint16_t min_pulse_us{500u};
    std::uint16_t max_pulse_us{2500u};

    [[nodiscard]] constexpr bool valid() const noexcept
    {
        return max_angle_deg > min_angle_deg &&
               min_pulse_us >= 500u &&
               max_pulse_us <= 2500u &&
               max_pulse_us > min_pulse_us;
    }
};

/**
 * @brief 角度 → 脉宽（线性插值）
 *
 *   ratio = (deg - min_angle) / (max_angle - min_angle)
 *   pulse = min_pulse + ratio * (max_pulse - min_pulse)
 *
 * 返回值：
 *   Ok               成功，pulse 写入 out
 *   InvalidArgument  标定非法、角度越界、计算结果越界
 */
[[nodiscard]] ServoStatus angleToPulseUs(const Sg90Calibration& cal,
                                         float deg,
                                         std::uint16_t& out) noexcept;

/**
 * @brief 脉宽 → 角度（反算，调试/标定用）
 */
[[nodiscard]] ServoStatus pulseUsToAngle(const Sg90Calibration& cal,
                                         std::uint16_t pulse_us,
                                         float& out) noexcept;

} // namespace module
