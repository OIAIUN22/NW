#pragma once

#include <cstdint>

namespace module {

enum class ServoStatus : std::uint8_t {
    Ok = 0,
    InvalidArgument,
    NotReady,
    Busy,
    InitFailed,
    BusError,
};

/**
 * @brief 舵机能力接口（C++17，纯虚接口）
 *
 * module/app 只依赖这个接口，不依赖 bsp_sg90 / HAL。
 * 具体实现（Sg90Servo）在 .cpp 里通过 extern "C" 调用 C 编译的 BSP。
 */
class IServo {
public:
    virtual ~IServo() = default;

    [[nodiscard]] virtual ServoStatus init() = 0;
    [[nodiscard]] virtual ServoStatus setAngle(float deg) = 0;
    [[nodiscard]] virtual ServoStatus setPulseUs(std::uint16_t us) = 0;
    [[nodiscard]] virtual ServoStatus disable() = 0;
    [[nodiscard]] virtual bool ready() const noexcept = 0;
};

} // namespace module
