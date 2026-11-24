#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <string_view>

namespace module::bsp {

/**
 * @brief BSP 适配层统一状态
 *
 * 所有 C BSP 的私有状态码都在 adapter 的 .cpp 里映射到这里，
 * module/app 不再看到 bsp_xxx_status_t。
 */
enum class Status : std::uint8_t {
    Ok = 0,
    InvalidArgument,
    NotReady,
    Busy,
    Timeout,
    BusError,
    InitFailed,
    NotSupported,
};

/**
 * @brief 只读字节视图（C++17 没有 std::span）
 *
 * 不拥有内存，调用期间 data 必须有效。
 */
struct ByteView {
    const std::uint8_t* data{nullptr};
    std::size_t size{0};

    constexpr ByteView() noexcept = default;
    constexpr ByteView(const std::uint8_t* d, std::size_t n) noexcept
        : data(d), size(n) {}

    [[nodiscard]] constexpr bool empty() const noexcept
    {
        return data == nullptr || size == 0;
    }
};

/**
 * @brief 标准帧数据（本项目的 CAN 纯发送只支持标准数据帧）
 */
struct CanFrame {
    std::uint32_t id{0};
    std::uint8_t len{0};
    std::array<std::uint8_t, 8> data{};
    bool extended{false};
    bool remote{false};
};

/**
 * @brief 所有 BSP 适配器的公共契约
 */
class IBspDevice {
public:
    virtual ~IBspDevice() = default;

    [[nodiscard]] virtual Status init() = 0;
    [[nodiscard]] virtual bool ready() const noexcept = 0;
    [[nodiscard]] virtual std::string_view name() const noexcept = 0;
};

} // namespace module::bsp
