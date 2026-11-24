#include "servo/sg90_servo.hpp"

/*
 * BSP 是 C 编译器编译的，函数符号是 C linkage。
 * 在 C++17 里用 extern "C" 包含 C 头，避免 C++ name mangling 对不上。
 */
extern "C" {
#include "pwm/bsp_sg90.h"
}

namespace module {
namespace {

bsp_sg90_channel_t toBspChannel(ServoChannel ch) noexcept
{
    return (ch == ServoChannel::Ch2) ? BSP_SG90_CH2 : BSP_SG90_CH1;
}

bool validChannel(ServoChannel ch) noexcept
{
    return ch == ServoChannel::Ch1 || ch == ServoChannel::Ch2;
}

ServoStatus mapStatus(bsp_sg90_status_t st) noexcept
{
    switch (st) {
    case BSP_SG90_OK:       return ServoStatus::Ok;
    case BSP_SG90_ERR_PARAM: return ServoStatus::InvalidArgument;
    case BSP_SG90_ERR_BUSY:  return ServoStatus::Busy;
    case BSP_SG90_ERR_INIT:  return ServoStatus::InitFailed;
    case BSP_SG90_ERR_STATE: return ServoStatus::NotReady;
    default:                 return ServoStatus::BusError;
    }
}

} // namespace

ServoStatus Sg90Servo::init()
{
    if (ready_) {
        return ServoStatus::Ok;
    }
    if (!cal_.valid()) {
        return ServoStatus::InvalidArgument;
    }

    const bsp_sg90_status_t st = bsp_sg90_init();
    if (st == BSP_SG90_OK || st == BSP_SG90_ERR_BUSY) {
        /*
         * BSP 是全局 TIM2 初始化：第二个 Sg90Servo 实例再 init 会得到 BUSY，
         * 这表示“已经初始化好了”，对模块来说等价于成功。
         */
        ready_ = true;
        return ServoStatus::Ok;
    }
    return mapStatus(st);
}

ServoStatus Sg90Servo::setAngle(float deg)
{
    if (!ready_) {
        return ServoStatus::NotReady;
    }
    if (!validChannel(ch_)) {
        return ServoStatus::InvalidArgument;
    }

    std::uint16_t pulse_us = 0u;
    const ServoStatus convert = angleToPulseUs(cal_, deg, pulse_us);
    if (convert != ServoStatus::Ok) {
        return convert;
    }

    return mapStatus(bsp_sg90_set_pulse_us(toBspChannel(ch_), pulse_us));
}

ServoStatus Sg90Servo::setPulseUs(std::uint16_t us)
{
    if (!ready_) {
        return ServoStatus::NotReady;
    }
    if (!validChannel(ch_)) {
        return ServoStatus::InvalidArgument;
    }

    return mapStatus(bsp_sg90_set_pulse_us(toBspChannel(ch_), us));
}

ServoStatus Sg90Servo::disable()
{
    if (!ready_) {
        return ServoStatus::NotReady;
    }
    if (!validChannel(ch_)) {
        return ServoStatus::InvalidArgument;
    }

    return mapStatus(bsp_sg90_disable(toBspChannel(ch_)));
}

bool Sg90Servo::ready() const noexcept
{
    return ready_;
}

} // namespace module
