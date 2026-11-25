#include "servo/servo_app.hpp"

namespace app {
namespace {

constexpr float kAngleEps = 0.01f;
constexpr std::uint32_t kMaxDtMs = 100u;

bool angleInRange(float deg, float lo, float hi) noexcept
{
    /* NaN 比较为 false，因此也会被拒绝 */
    return deg >= lo && deg <= hi;
}

bool configValid(const ServoConfig& cfg) noexcept
{
    return cfg.max_angle_deg > cfg.min_angle_deg &&
           cfg.safe_angle_deg >= cfg.min_angle_deg &&
           cfg.safe_angle_deg <= cfg.max_angle_deg &&
           cfg.max_speed_deg_per_s > 0.0f &&
           cfg.command_timeout_ms > 0u &&
           cfg.max_consecutive_errors > 0u;
}

float moveToward(float current, float target, float max_step) noexcept
{
    if (target > current + max_step) {
        return current + max_step;
    }
    if (target < current - max_step) {
        return current - max_step;
    }
    return target;
}

} // namespace

bool ServoApp::init(std::uint32_t now_ms)
{
    if (state_ == ServoState::EStopped) {
        return false; // 急停后必须复位/重新上电
    }
    if (state_ == ServoState::Ready || state_ == ServoState::Moving) {
        return true;
    }
    if (!configValid(cfg_)) {
        state_ = ServoState::Fault;
        return false;
    }

    if (servo_.init() != module::ServoStatus::Ok) {
        state_ = ServoState::Fault;
        error_count_ = 1u;
        return false;
    }

    current_deg_ = cfg_.safe_angle_deg;
    target_deg_ = cfg_.safe_angle_deg;
    last_cmd_ms_ = now_ms;
    last_update_ms_ = now_ms;

    if (!applyAngle(current_deg_)) {
        enterFault();
        return false;
    }

    error_count_ = 0u;
    state_ = ServoState::Ready;
    return true;
}

bool ServoApp::setTarget(float deg, std::uint32_t now_ms) noexcept
{
    if (state_ == ServoState::Init ||
        state_ == ServoState::Fault ||
        state_ == ServoState::EStopped) {
        return false;
    }
    if (!angleInRange(deg, cfg_.min_angle_deg, cfg_.max_angle_deg)) {
        return false;
    }

    target_deg_ = deg;
    last_cmd_ms_ = now_ms;
    state_ = ServoState::Moving;
    return true;
}

void ServoApp::update(std::uint32_t now_ms) noexcept
{
    if (state_ == ServoState::Init ||
        state_ == ServoState::Fault ||
        state_ == ServoState::EStopped) {
        return;
    }

    std::uint32_t dt = now_ms - last_update_ms_;
    if (dt == 0u) {
        return;
    }
    last_update_ms_ = now_ms;
    if (dt > kMaxDtMs) {
        dt = kMaxDtMs; // 调试暂停后不要一步跳到目标
    }

    /* 命令超时：回安全角，进入 Safe */
    const std::uint32_t since_cmd = now_ms - last_cmd_ms_;
    if (since_cmd >= cfg_.command_timeout_ms &&
        target_deg_ != cfg_.safe_angle_deg) {
        target_deg_ = cfg_.safe_angle_deg;
        state_ = ServoState::Safe;
    }

    /* 斜率限制：每 ms 最多走 max_speed 度 */
    const float max_step =
        cfg_.max_speed_deg_per_s * (static_cast<float>(dt) / 1000.0f);
    const float next = moveToward(current_deg_, target_deg_, max_step);

    if (next != current_deg_) {
        if (!applyAngle(next)) {
            if (error_count_ < 255u) {
                ++error_count_;
            }
            if (error_count_ >= cfg_.max_consecutive_errors) {
                enterFault();
            }
            return;
        }

        current_deg_ = next;
        error_count_ = 0u;
    }

    /* 到达目标 */
    const float diff = target_deg_ - current_deg_;
    const float abs_diff = (diff < 0.0f) ? -diff : diff;
    if (abs_diff <= kAngleEps && state_ == ServoState::Moving) {
        state_ = ServoState::Ready;
    }
}

void ServoApp::emergencyStop() noexcept
{
    state_ = ServoState::EStopped;
    target_deg_ = current_deg_;
    (void)servo_.disable();
}

bool ServoApp::clearFault(std::uint32_t now_ms) noexcept
{
    if (state_ != ServoState::Fault) {
        return false;
    }

    if (!applyAngle(cfg_.safe_angle_deg)) {
        return false;
    }

    current_deg_ = cfg_.safe_angle_deg;
    target_deg_ = cfg_.safe_angle_deg;
    error_count_ = 0u;
    last_cmd_ms_ = now_ms;
    last_update_ms_ = now_ms;
    state_ = ServoState::Ready;
    return true;
}

bool ServoApp::applyAngle(float deg) noexcept
{
    return servo_.setAngle(deg) == module::ServoStatus::Ok;
}

void ServoApp::enterFault() noexcept
{
    state_ = ServoState::Fault;
    target_deg_ = cfg_.safe_angle_deg;

    /* 尽力回安全角；如果总线错误，这次也可能失败 */
    if (applyAngle(cfg_.safe_angle_deg)) {
        current_deg_ = cfg_.safe_angle_deg;
    }
}

} // namespace app
