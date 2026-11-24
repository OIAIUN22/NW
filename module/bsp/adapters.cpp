#include "bsp/adapters.hpp"

/*
 * BSP 是 C 编译器编译的，函数符号是 C linkage。
 * 只在 adapter 的 .cpp 里包含 C 头，接口头文件保持纯 C++。
 */
extern "C" {
#include "uart/bsp_uart_tx.h"
#include "i2c/bsp_i2c_tx.h"
#include "can/bsp_can_tx.h"
}

namespace module::bsp {
namespace {

Status mapUart(bsp_uart_tx_status_t st) noexcept
{
    switch (st) {
    case BSP_UART_TX_OK:        return Status::Ok;
    case BSP_UART_TX_ERR_PARAM: return Status::InvalidArgument;
    case BSP_UART_TX_ERR_INIT:  return Status::InitFailed;
    case BSP_UART_TX_ERR_BUSY:  return Status::Busy;
    case BSP_UART_TX_ERR_TIMEOUT: return Status::Timeout;
    case BSP_UART_TX_ERR_BUS:   return Status::BusError;
    default:                    return Status::BusError;
    }
}

Status mapI2c(bsp_i2c_tx_status_t st) noexcept
{
    switch (st) {
    case BSP_I2C_TX_OK:         return Status::Ok;
    case BSP_I2C_TX_ERR_PARAM:  return Status::InvalidArgument;
    case BSP_I2C_TX_ERR_INIT:   return Status::InitFailed;
    case BSP_I2C_TX_ERR_BUSY:   return Status::Busy;
    case BSP_I2C_TX_ERR_TIMEOUT: return Status::Timeout;
    case BSP_I2C_TX_ERR_BUS:    return Status::BusError;
    default:                    return Status::BusError;
    }
}

Status mapCan(bsp_can_tx_status_t st) noexcept
{
    switch (st) {
    case BSP_CAN_TX_OK:         return Status::Ok;
    case BSP_CAN_TX_ERR_PARAM:  return Status::InvalidArgument;
    case BSP_CAN_TX_ERR_INIT:   return Status::InitFailed;
    case BSP_CAN_TX_ERR_BUSY:   return Status::Busy;
    case BSP_CAN_TX_ERR_TIMEOUT: return Status::Timeout;
    case BSP_CAN_TX_ERR_BUS:    return Status::BusError;
    default:                    return Status::BusError;
    }
}

} // namespace

/* ---------------- UART ---------------- */

Status UartTxAdapter::init()
{
    const auto st = bsp_uart_tx_init();
    if (st == BSP_UART_TX_OK) {
        return Status::Ok;
    }
    if (st == BSP_UART_TX_ERR_BUSY && ready()) {
        return Status::Ok;
    }
    return mapUart(st);
}

bool UartTxAdapter::ready() const noexcept
{
    return bsp_uart_tx_is_ready() != 0u;
}

std::string_view UartTxAdapter::name() const noexcept
{
    return "uart1";
}

Status UartTxAdapter::write(ByteView data, std::uint32_t timeout_ms)
{
    if (data.empty() || data.size > 0xFFFFu) {
        return Status::InvalidArgument;
    }

    return mapUart(bsp_uart_tx_send(
        data.data, static_cast<std::uint16_t>(data.size), timeout_ms));
}

/* ---------------- I2C ---------------- */

Status I2cTxAdapter::init()
{
    const auto st = bsp_i2c_tx_init();
    if (st == BSP_I2C_TX_OK) {
        return Status::Ok;
    }
    if (st == BSP_I2C_TX_ERR_BUSY && ready()) {
        return Status::Ok;
    }
    return mapI2c(st);
}

bool I2cTxAdapter::ready() const noexcept
{
    return bsp_i2c_tx_is_ready() != 0u;
}

std::string_view I2cTxAdapter::name() const noexcept
{
    return "i2c1";
}

Status I2cTxAdapter::write(std::uint8_t addr7,
                           ByteView data,
                           std::uint32_t timeout_ms)
{
    if (addr7 > 0x7Fu || data.empty() || data.size > 0xFFFFu) {
        return Status::InvalidArgument;
    }

    return mapI2c(bsp_i2c_tx_write(
        addr7, data.data, static_cast<std::uint16_t>(data.size), timeout_ms));
}

Status I2cTxAdapter::writeReg(std::uint8_t addr7,
                              std::uint8_t reg,
                              ByteView data,
                              std::uint32_t timeout_ms)
{
    if (addr7 > 0x7Fu || data.empty() || data.size > 0xFFFFu) {
        return Status::InvalidArgument;
    }

    return mapI2c(bsp_i2c_tx_write_reg(
        addr7, reg, data.data, static_cast<std::uint16_t>(data.size), timeout_ms));
}

/* ---------------- CAN ---------------- */

Status CanTxAdapter::init()
{
    const auto st = bsp_can_tx_init();
    if (st == BSP_CAN_TX_OK) {
        return Status::Ok;
    }
    if (st == BSP_CAN_TX_ERR_BUSY && ready()) {
        return Status::Ok;
    }
    return mapCan(st);
}

bool CanTxAdapter::ready() const noexcept
{
    return bsp_can_tx_is_ready() != 0u;
}

std::string_view CanTxAdapter::name() const noexcept
{
    return "can1";
}

Status CanTxAdapter::send(const CanFrame& frame, std::uint32_t timeout_ms)
{
    if (frame.extended || frame.remote) {
        return Status::NotSupported; // 当前 BSP 只发标准数据帧
    }
    if (frame.id > 0x7FFu || frame.len != 8u) {
        return Status::InvalidArgument; // 当前 BSP 固定 8 字节
    }

    return mapCan(bsp_can_tx_send(frame.id, frame.data.data(), timeout_ms));
}

} // namespace module::bsp
