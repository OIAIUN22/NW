#pragma once

#include "bsp/i_bus.hpp"

namespace module::bsp {

/**
 * @brief 把 C 编译的 bsp_uart_tx 适配成 IUart
 */
class UartTxAdapter final : public IUart {
public:
    [[nodiscard]] Status init() override;
    [[nodiscard]] bool ready() const noexcept override;
    [[nodiscard]] std::string_view name() const noexcept override;
    [[nodiscard]] Status write(ByteView data,
                               std::uint32_t timeout_ms) override;
};

/**
 * @brief 把 C 编译的 bsp_i2c_tx 适配成 II2c
 */
class I2cTxAdapter final : public II2c {
public:
    [[nodiscard]] Status init() override;
    [[nodiscard]] bool ready() const noexcept override;
    [[nodiscard]] std::string_view name() const noexcept override;
    [[nodiscard]] Status write(std::uint8_t addr7,
                               ByteView data,
                               std::uint32_t timeout_ms) override;
    [[nodiscard]] Status writeReg(std::uint8_t addr7,
                                  std::uint8_t reg,
                                  ByteView data,
                                  std::uint32_t timeout_ms) override;
};

/**
 * @brief 把 C 编译的 bsp_can_tx 适配成 ICan
 */
class CanTxAdapter final : public ICan {
public:
    [[nodiscard]] Status init() override;
    [[nodiscard]] bool ready() const noexcept override;
    [[nodiscard]] std::string_view name() const noexcept override;
    [[nodiscard]] Status send(const CanFrame& frame,
                              std::uint32_t timeout_ms) override;
};

} // namespace module::bsp
