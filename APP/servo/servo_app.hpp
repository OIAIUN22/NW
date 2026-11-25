#pragma once

#include <cstdint>

#include "interfaces/i_servo.hpp"

namespace app {

enum class ServoState : std::uint8_t {
    Init = 0,
    Ready,
    Moving,
    Safe,
    Fault,
    EStopped,
};

struct ServoConfig {
    float min_angle_deg{15.0f};        /* 软限位，别顶机械限位 */
    float max_angle_deg{165.0f};
    float safe_angle_deg{90.0f};       /* 超时/故障回中 */
    float max_speed_deg_per_s{120.0f}; /* 最大角速度 */
    std::uint32_t command_timeout_ms{500u};
    std::uint8_t max_consecutive_errors{3u};
};

/**
 * @brief APP 层舵机保护
 *
 * 负责：
 *   - 软件限位：只接受 [min, max]；
 *   - 斜率限制：按 max_speed_deg_per_s 逐步逼近目标；
 *   - 命令超时：超时回 safe_angle；
 *   - 连续错误：进入 Fault，尝试回安全角；
 *   - 急停：进入 EStopped，关闭 PWM。
 *
 * 不负责：
 *   - 角度→脉宽换算（module）；
 *   - TIM2/PWM（BSP）；
 *   - 电源/机械限位开关（硬件）。
 *
 * 所有 now_ms 由调用方传入，APP 不依赖 HAL_GetTick。
 */
class ServoApp final {
public:
    explicit ServoApp(module::IServo& servo,
                      ServoConfig cfg = {}) noexcept
        : servo_(servo), cfg_(cfg) {}

    /**
      * @brief 初始化舵机并回到安全角
      * @return true 成功；false 失败，状态为 Fault
      */
    [[nodiscard]] bool init(std::uint32_t now_ms);

    /**
      * @brief 设置目标角度
      * @return false：状态不允许、角度越界或 NaN
      */
    [[nodiscard]] bool setTarget(float deg, std::uint32_t now_ms) noexcept;

    /**
      * @brief 周期调用，建议 10ms 一次
      */
    void update(std::uint32_t now_ms) noexcept;

    /**
      * @brief 急停：关闭 PWM，状态锁存为 EStopped
      */
    void emergencyStop() noexcept;

    /**
      * @brief 从 Fault 恢复；EStopped 不允许软件恢复
      */
    [[nodiscard]] bool clearFault(std::uint32_t now_ms) noexcept;

    [[nodiscard]] ServoState state() const noexcept { return state_; }
    [[nodiscard]] float currentAngle() const noexcept { return current_deg_; }
    [[nodiscard]] float targetAngle() const noexcept { return target_deg_; }
    [[nodiscard]] std::uint8_t errorCount() const noexcept { return error_count_; }

private:
    [[nodiscard]] bool applyAngle(float deg) noexcept;
    void enterFault() noexcept;

    module::IServo& servo_;
    ServoConfig cfg_;
    ServoState state_{ServoState::Init};

    float current_deg_{0.0f};
    float target_deg_{0.0f};
    std::uint32_t last_cmd_ms_{0};
    std::uint32_t last_update_ms_{0};
    std::uint8_t error_count_{0};
};

} // namespace app
