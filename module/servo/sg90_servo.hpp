#pragma once

#include "interfaces/i_servo.hpp"
#include "servo/sg90_angle.hpp"

namespace module {

enum class ServoChannel : std::uint8_t {
    Ch1 = 0,   /* BSP: PA0 / TIM2_CH1 */
    Ch2 = 1,   /* BSP: PA1 / TIM2_CH2 */
};

/**
 * @brief SG90 舵机模块
 *
 * 这是 C++17 的 module 层实现：
 *   - 角度→脉宽算法在 module（sg90_angle），不依赖 BSP；
 *   - 对下层通过 extern "C" 调用 C 编译的 bsp_sg90；
 *   - 不把 bsp_sg90_channel_t / BSP 状态码泄漏到 module/app。
 */
class Sg90Servo final : public IServo {
public:
    explicit Sg90Servo(ServoChannel ch,
                       Sg90Calibration cal = {}) noexcept
        : ch_(ch), cal_(cal) {}

    [[nodiscard]] ServoStatus init() override;
    [[nodiscard]] ServoStatus setAngle(float deg) override;
    [[nodiscard]] ServoStatus setPulseUs(std::uint16_t us) override;
    [[nodiscard]] ServoStatus disable() override;
    [[nodiscard]] bool ready() const noexcept override;

private:
    ServoChannel ch_;
    Sg90Calibration cal_;
    bool ready_{false};
};

} // namespace module
