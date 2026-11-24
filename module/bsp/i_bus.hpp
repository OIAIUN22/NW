#pragma once

#include "bsp/types.hpp"

namespace module::bsp {

/**
 * @brief UART 能力接口（当前 BSP 只实现发送）
 */
class IUart : public IBspDevice {
public:
    [[nodiscard]] virtual Status write(ByteView data,
                                       std::uint32_t timeout_ms) = 0;
};

/**
 * @brief I2C 能力接口（当前 BSP 只实现写）
 *
 * addr7 是 7 位从机地址，adapter 内部负责左移。
 */
class II2c : public IBspDevice {
public:
    [[nodiscard]] virtual Status write(std::uint8_t addr7,
                                       ByteView data,
                                       std::uint32_t timeout_ms) = 0;

    [[nodiscard]] virtual Status writeReg(std::uint8_t addr7,
                                          std::uint8_t reg,
                                          ByteView data,
                                          std::uint32_t timeout_ms) = 0;
};

/**
 * @brief CAN 能力接口（当前 BSP 只实现标准数据帧发送）
 */
class ICan : public IBspDevice {
public:
    [[nodiscard]] virtual Status send(const CanFrame& frame,
                                      std::uint32_t timeout_ms) = 0;
};

} // namespace module::bsp
