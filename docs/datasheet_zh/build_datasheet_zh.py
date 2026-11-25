from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from pathlib import Path

OUT = Path(r"D:\Users\Asus\Documents\NW\docs\datasheet_zh")
OUT.mkdir(parents=True, exist_ok=True)

BODY_FONT = "宋体"
HEAD_FONT = "微软雅黑"
MONO_FONT = "Consolas"


def set_run_font(run, name=BODY_FONT, size=10.5, bold=None, color=None):
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if color is not None:
        run.font.color.rgb = RGBColor(*color)


def style_font(style, name=BODY_FONT, size=10.5, bold=None, color=None):
    style.font.name = name
    style._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    style.font.size = Pt(size)
    if bold is not None:
        style.font.bold = bold
    if color is not None:
        style.font.color.rgb = RGBColor(*color)


def add_heading(doc, text, level=1):
    p = doc.add_paragraph(style=f"Heading {level}")
    run = p.add_run(text)
    if level == 1:
        set_run_font(run, HEAD_FONT, 17, True, (0x1F, 0x3A, 0x5F))
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(8)
    elif level == 2:
        set_run_font(run, HEAD_FONT, 13, True, (0x1F, 0x3A, 0x5F))
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
    else:
        set_run_font(run, HEAD_FONT, 11.5, True, (0x33, 0x33, 0x33))
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(3)
    return p


def add_p(doc, text, size=10.5, bold=False, align=None, space_after=4):
    p = doc.add_paragraph()
    run = p.add_run(text)
    set_run_font(run, BODY_FONT, size, bold)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.35
    if align is not None:
        p.alignment = align
    return p


def add_bullet(doc, text, level=0):
    p = doc.add_paragraph(style="List Bullet")
    run = p.add_run(text)
    set_run_font(run, BODY_FONT, 10.5)
    p.paragraph_format.left_indent = Cm(0.75 + 0.6 * level)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.25
    return p


def shade_cell(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def set_cell_text(cell, text, bold=False, size=8.5, color=None, align=None):
    cell.text = ""
    p = cell.paragraphs[0]
    run = p.add_run(str(text))
    set_run_font(run, BODY_FONT, size, bold, color)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.05
    if align is not None:
        p.alignment = align


def add_table(doc, headers, rows, widths=None, font_size=8.5, header_color="1F3A5F"):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        set_cell_text(hdr[i], h, True, font_size, (255, 255, 255),
                      WD_ALIGN_PARAGRAPH.CENTER)
        shade_cell(hdr[i], header_color)
    for row in rows:
        cells = table.add_row().cells
        for i, v in enumerate(row):
            set_cell_text(cells[i], v, False, font_size)
    if widths:
        for row in table.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
    # repeat header row across pages
    trPr = table.rows[0]._tr.get_or_add_trPr()
    tblHeader = OxmlElement("w:tblHeader")
    tblHeader.set(qn("w:val"), "true")
    trPr.append(tblHeader)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return table


def add_caption(doc, text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    set_run_font(run, HEAD_FONT, 9, False, (0x55, 0x55, 0x55))
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(6)


def add_note_box(doc, title, lines):
    table = doc.add_table(rows=1, cols=1)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    shade_cell(cell, "F2F5F9")
    cell.text = ""
    p = cell.paragraphs[0]
    r = p.add_run(title)
    set_run_font(r, HEAD_FONT, 10, True, (0x1F, 0x3A, 0x5F))
    for line in lines:
        p2 = cell.add_paragraph()
        r2 = p2.add_run(line)
        set_run_font(r2, BODY_FONT, 9.5)
        p2.paragraph_format.space_after = Pt(1)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def add_page_number_footer(section):
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("STM32F103x8/xB 数据手册 中文翻译版    ")
    set_run_font(r, HEAD_FONT, 8, False, (0x77, 0x77, 0x77))

    fldChar1 = OxmlElement("w:fldChar")
    fldChar1.set(qn("w:fldCharType"), "begin")
    instrText = OxmlElement("w:instrText")
    instrText.set(qn("xml:space"), "preserve")
    instrText.text = " PAGE "
    fldChar2 = OxmlElement("w:fldChar")
    fldChar2.set(qn("w:fldCharType"), "end")
    r2 = p.add_run()
    r2._r.append(fldChar1)
    r2._r.append(instrText)
    r2._r.append(fldChar2)
    set_run_font(r2, HEAD_FONT, 8, False, (0x77, 0x77, 0x77))


doc = Document()
section = doc.sections[0]
section.page_width = Cm(21.0)
section.page_height = Cm(29.7)
section.top_margin = Cm(2.0)
section.bottom_margin = Cm(2.0)
section.left_margin = Cm(2.2)
section.right_margin = Cm(2.0)

styles = doc.styles
style_font(styles["Normal"], BODY_FONT, 10.5)
style_font(styles["Heading 1"], HEAD_FONT, 17, True)
style_font(styles["Heading 2"], HEAD_FONT, 13, True)
style_font(styles["Heading 3"], HEAD_FONT, 11.5, True)
styles["Normal"].paragraph_format.line_spacing = 1.35

add_page_number_footer(section)
doc.core_properties.title = "STM32F103x8/STM32F103xB 数据手册 中文翻译版"
doc.core_properties.subject = "DS5319 Rev 18 中文技术翻译"
doc.core_properties.author = "中文技术翻译版"

# ---------------- Cover ----------------
for _ in range(3):
    doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("STM32F103x8 / STM32F103xB")
set_run_font(r, HEAD_FONT, 26, True, (0x1F, 0x3A, 0x5F))

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("中密度性能系列 32 位微控制器")
set_run_font(r, HEAD_FONT, 16, True, (0x33, 0x33, 0x33))

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("数据手册 · 中文翻译版")
set_run_font(r, HEAD_FONT, 18, True, (0xB0, 0x3A, 0x2E))

for _ in range(2):
    doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("基于 STMicroelectronics DS5319 Rev 18（2022 年 3 月）")
set_run_font(r, BODY_FONT, 11, False, (0x55, 0x55, 0x55))

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("64/128 KB Flash · 20 KB SRAM · USB · CAN · 7 个定时器 · 2 个 ADC · 9 个通信接口")
set_run_font(r, BODY_FONT, 9.5, False, (0x55, 0x55, 0x55))

for _ in range(4):
    doc.add_paragraph()

add_note_box(doc, "翻译说明", [
    "1. 本文件是英文数据手册的中文技术翻译版，不是 STMicroelectronics 官方中文版。",
    "2. 技术参数、封装尺寸、订购代码与法律声明，请以英文原版 DS5319 Rev 18 为准。",
    "3. 为便于阅读，正文采用意译；表格保留原始数值和单位。Flash、SRAM、GPIO、USART、",
    "   SPI、I²C、CAN、USB、ADC、PWM、SWD、JTAG 等术语保留英文缩写。",
    "4. 原版中的框图、曲线图和封装机械图未逐页复制；关键表格已翻译，完整图形请对照原版。",
    "5. 原版共 116 页；本版是技术精译（保留全部章节与关键表格），不是逐页影印翻译。",
    "6. 本翻译版适合学习、选型和嵌入式开发参考，不替代原版做正式认证或生产依据。",
])

doc.add_page_break()

# ---------------- TOC ----------------
add_heading(doc, "目录", 1)
toc = [
    ("1", "引言", "9"),
    ("2", "描述", "9"),
    ("2.1", "器件概览", "10"),
    ("2.2", "全系列兼容性", "13"),
    ("2.3", "功能概述", "14"),
    ("3", "引脚定义", "21"),
    ("3.1", "封装与引脚图", "21"),
    ("3.2", "LQFP48 引脚表", "28"),
    ("3.3", "引脚使用注意事项", "33"),
    ("4", "存储器映射", "34"),
    ("5", "电气特性", "35"),
    ("5.1", "参数条件", "35"),
    ("5.2", "绝对最大额定值", "37"),
    ("5.3", "工作条件", "38"),
    ("5.3.1", "通用工作条件", "38"),
    ("5.3.2", "上电/掉电条件", "39"),
    ("5.3.3", "复位与电源控制", "39"),
    ("5.3.4", "内部参考电压", "40"),
    ("5.3.5", "供电电流", "40"),
    ("5.3.6", "外部时钟", "50"),
    ("5.3.7", "内部时钟", "54"),
    ("5.3.8", "PLL", "56"),
    ("5.3.9", "存储器特性", "56"),
    ("5.3.10", "EMC 特性", "57"),
    ("5.3.11", "ESD 与电气敏感性", "59"),
    ("5.3.12", "I/O 电流注入", "60"),
    ("5.3.13", "I/O 端口特性", "61"),
    ("5.3.14", "NRST 引脚", "66"),
    ("5.3.15", "TIM 定时器", "67"),
    ("5.3.16", "通信接口", "68"),
    ("5.3.17", "CAN 接口", "73"),
    ("5.3.18", "12 位 ADC", "74"),
    ("5.3.19", "温度传感器", "78"),
    ("6", "封装信息", "79"),
    ("6.1", "LQFP48 封装", "101"),
    ("6.2", "热特性", "104"),
    ("7", "订购信息", "107"),
    ("8", "版本历史", "108"),
    ("A", "术语表", "—"),
]
for num, title, page in toc:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    run = p.add_run(f"{num}  {title}")
    set_run_font(run, BODY_FONT, 9.5, num.count(".") == 0)
    if page != "—":
        run2 = p.add_run(f"  （原版 p.{page}）")
        set_run_font(run2, BODY_FONT, 8.0, False, (0x77, 0x77, 0x77))

doc.add_page_break()

# ---------------- 1 Introduction ----------------
add_heading(doc, "1  引言  Introduction", 1)
add_p(doc, "本文档给出 STM32F103x8 与 STM32F103xB 中密度性能系列微控制器的订购信息和机械特性。若要了解整个 STM32F103xx 系列的更多细节，请参阅第 2.2 节“全系列兼容性”。")
add_p(doc, "阅读本数据手册时，应同时参考 STM32F10xxx 低密度、中密度和高密度参考手册。参考手册与 Flash 编程手册可在 STMicroelectronics 网站 www.st.com 获取。")
add_p(doc, "关于 Arm® Cortex®-M3 内核，请参阅 Arm 网站 www.arm.com 提供的 Cortex®-M3 技术参考手册。")
add_note_box(doc, "阅读建议", [
    "数据手册回答“芯片有哪些资源、引脚怎么接、电气参数是多少”。",
    "参考手册回答“寄存器怎么配置、外设怎么工作”。",
    "两者配合使用：先用数据手册完成选型/原理图，再用参考手册写驱动。",
])

# ---------------- 2 Description ----------------
add_heading(doc, "2  描述  Description", 1)
add_p(doc, "STM32F103xx 中密度性能系列采用高性能 Arm® Cortex®-M3 32 位 RISC 内核，最高工作频率 72 MHz；片上集成高速存储器（Flash 最大 128 KB，SRAM 最大 20 KB），并通过两条 APB 总线连接丰富的外设。")
add_p(doc, "全系列均提供 2 个 12 位 ADC、3 个通用 16 位定时器、1 个 PWM 定时器，以及标准和高级通信接口：最多 2 个 I²C、2 个 SPI、3 个 USART、1 个 USB 和 1 个 CAN。")
add_p(doc, "器件工作电压为 2.0 V 至 3.6 V，提供 –40 °C 至 +85 °C 和 –40 °C 至 +105 °C 两种温度范围。多种低功耗模式可用于低功耗设计。")
add_p(doc, "该系列提供 36 引脚至 100 引脚共六种封装。不同型号包含的外设组合不同；下文给出整个系列外设的总体介绍。")

add_heading(doc, "2.1  器件概览  Device overview", 2)
add_p(doc, "表 2 汇总了中密度 STM32F103xx 的存储器、定时器、通信接口、GPIO 和 ADC 资源。")
add_caption(doc, "表 2  STM32F103xx 中密度器件特性与外设数量")
add_table(doc,
          ["外设 / 参数", "STM32F103Tx", "STM32F103Cx", "STM32F103Rx", "STM32F103Vx"],
          [
              ["Flash（KB）", "64 / 128", "64 / 128", "64 / 128", "64 / 128"],
              ["SRAM（KB）", "20", "20", "20", "20"],
              ["通用定时器", "3", "3", "3", "3"],
              ["高级控制定时器", "1", "1", "1", "1"],
              ["SPI", "1", "2", "2", "2"],
              ["I²C", "1", "2", "2", "2"],
              ["USART", "2", "3", "3", "3"],
              ["USB", "1", "1", "1", "1"],
              ["CAN", "1", "1", "1", "1"],
              ["GPIO", "26", "37", "51", "80"],
              ["12 位 ADC", "2 个", "2 个", "2 个", "2 个"],
              ["ADC 通道", "10", "10", "16", "16"],
              ["CPU 频率", "72 MHz", "72 MHz", "72 MHz", "72 MHz"],
              ["工作电压", "2.0–3.6 V", "2.0–3.6 V", "2.0–3.6 V", "2.0–3.6 V"],
              ["环境温度", "–40…+85 / +105 °C", "同左", "同左", "同左"],
              ["结温", "–40…+125 °C", "同左", "同左", "同左"],
              ["封装", "VFQFPN36", "LQFP48 / UFQFPN48", "LQFP64 / TFBGA64", "LQFP100 / LFBGA100 / UFBGA100"],
          ],
          widths=[3.0, 3.0, 3.4, 3.7, 4.3])
add_p(doc, "注：TFBGA64 封装只有 15 个 ADC 通道可用，因为有一个模拟输入引脚被 VREF+ 取代。", 8.5)

add_heading(doc, "2.2  全系列兼容性  Full compatibility", 2)
add_p(doc, "STM32F103xx 是一个完整系列，成员之间在引脚、软件和功能上完全兼容。参考手册中：")
add_bullet(doc, "STM32F103x4、STM32F103x6：低密度器件；")
add_bullet(doc, "STM32F103x8、STM32F103xB：中密度器件，也就是本手册的对象；")
add_bullet(doc, "STM32F103xC、STM32F103xD、STM32F103xE：高密度器件。")
add_p(doc, "低密度和高密度器件是 STM32F103x8/B 的扩展型号，分别见 STM32F103x4/6 与 STM32F103xC/D/E 数据手册。低密度器件 Flash/RAM 更小、定时器和外设更少；高密度器件 Flash/RAM 更大，并增加 SDIO、FSMC、I²S、DAC 等外设，但仍保持兼容。")
add_p(doc, "STM32F103x4/x6/xC/xD/xE 可作为 STM32F103x8/B 的“直接替换”，方便在开发周期中调整存储器容量。STM32F103xx 性能系列还与 STM32F101xx 访问线和 STM32F102xx USB 访问线完全兼容。")
add_p(doc, "表 3 给出系列按引脚数和 Flash 容量的划分。对于常见的 STM32F103C8T6：48 引脚、64 KB Flash、20 KB SRAM、中密度。", 9.5)
add_caption(doc, "表 3  STM32F103xx 系列划分（节选）")
add_table(doc, ["引脚", "低密度 16/32 KB", "中密度 64 KB", "中密度 128 KB", "高密度 256/384/512 KB"], [
    ["36", "16/32 KB Flash，6/10 KB RAM", "64 KB，20 KB", "—", "—"],
    ["48", "16/32 KB，6/10 KB", "64 KB，20 KB", "128 KB，20 KB", "—"],
    ["64", "—", "64 KB，20 KB", "128 KB，20 KB", "—"],
    ["100", "—", "—", "128 KB，20 KB", "256/384/512 KB，48/64 KB"],
    ["144", "—", "—", "—", "512 KB，64 KB"],
], widths=[1.8, 4.8, 3.8, 3.8, 5.0], font_size=8.0)
add_p(doc, "注：表中只列出 Flash/RAM 和引脚关系；外设数量随型号变化，完整对照见原版表 2、表 3。", 8.8)

add_heading(doc, "2.3  功能概述  Overview", 2)
add_heading(doc, "2.3.1  Arm® Cortex®-M3 内核与嵌入式 Flash/SRAM", 3)
add_p(doc, "Arm® Cortex®-M3 是面向嵌入式系统的新一代 Arm 处理器，具有引脚少、功耗低、计算性能强、中断响应快等特点。它采用 32 位 RISC 架构，代码效率高，能在 8/16 位单片机常见的存储容量下提供 Arm 内核的性能。")
add_p(doc, "STM32F103xx 性能系列内嵌 Cortex®-M3，因此兼容 Arm 工具链和软件。图 1（原版第 11 页）给出器件总体框图。")

add_heading(doc, "2.3.2  嵌入式 Flash", 3)
add_p(doc, "片上 64 KB 或 128 KB Flash 用于存放程序和数据。Flash 支持页擦除、全片擦除、16 位编程；具体编程时间、擦除时间、擦写次数和数据保持见 5.3.9 节。")

add_heading(doc, "2.3.3  CRC 计算单元", 3)
add_p(doc, "CRC（循环冗余校验）单元用固定生成多项式对 32 位数据字计算 CRC 码。它可用于验证数据传输/存储完整性；在 EN/IEC 60335-1 标准范围内，也可用于校验 Flash 完整性。运行时计算的软件签名可与链接时生成并存放在指定地址的参考签名比较。")

add_heading(doc, "2.3.4  嵌入式 SRAM", 3)
add_p(doc, "20 KB 嵌入式 SRAM，CPU 以零等待状态读写，访问速度与 CPU 时钟相同。")

add_heading(doc, "2.3.5  嵌套向量中断控制器 NVIC", 3)
add_p(doc, "NVIC 可处理最多 43 个可屏蔽中断通道（不含 Cortex®-M3 的 16 个中断线）和 16 个优先级。特性包括：低延迟中断处理、中断向量表地址直接传给内核、紧密耦合内核接口、支持尾链（tail-chaining）、自动保存/恢复处理器状态、退出中断无额外指令开销。")

add_heading(doc, "2.3.6  外部中断/事件控制器 EXTI", 3)
add_p(doc, "EXTI 由 19 条边沿检测线组成，可独立配置上升沿、下降沿或双边沿触发，并可独立屏蔽。挂起寄存器保存中断请求状态。EXTI 能检测窄于内部 APB2 时钟周期的外部脉冲；最多 80 个 GPIO 可连接到 16 条外部中断线。")

add_heading(doc, "2.3.7  时钟与启动", 3)
add_p(doc, "启动时选择系统时钟，但复位后默认使用内部 8 MHz RC 振荡器作为 CPU 时钟。也可选择 4–16 MHz 外部时钟，并对其做失效监测；检测到失效时自动切回内部 RC，并在使能时产生软件中断。PLL 时钟输入也有完整的中断管理。")
add_p(doc, "多个预分频器可配置 AHB、高速 APB2 和低速 APB1 域。AHB/APB2 最高 72 MHz，APB1 最高 36 MHz。时钟树见原版图 2。")

add_heading(doc, "2.3.8  启动模式", 3)
add_p(doc, "启动时 BOOT 引脚选择三种启动方式之一：从用户 Flash 启动、从系统存储器启动、从嵌入式 SRAM 启动。Bootloader 位于系统存储器，可通过 USART1 重新编程 Flash；细节见 AN2606。")
add_table(doc, ["BOOT1", "BOOT0", "启动区域"], [
    ["x", "0", "用户 Flash"],
    ["0", "1", "系统存储器（Bootloader）"],
    ["1", "1", "嵌入式 SRAM"],
], widths=[3.0, 3.0, 8.0])
add_p(doc, "注：BOOT0 不能悬空；产品中通常用 10 kΩ 下拉到 GND，需要升级时再拉高。", 9.2)

add_heading(doc, "2.3.9  电源方案", 3)
add_bullet(doc, "VDD = 2.0–3.6 V：I/O 和内部稳压器的主电源，通过 VDD 引脚外部供电。")
add_bullet(doc, "VSSA、VDDA = 2.0–3.6 V：ADC、复位、RC、PLL 的模拟电源；使用 ADC 时 VDDA 最小 2.4 V。VDDA/VSSA 必须分别连接到 VDD/VSS。")
add_bullet(doc, "VBAT = 1.8–3.6 V：VDD 掉电时，为 RTC、32 kHz 外部振荡器和备份寄存器供电。")
add_p(doc, "电源引脚的去耦和连接方式见原版图 14。每个 VDD/VSS 对都要接 100 nF 陶瓷电容，VDDA 额外接 1 µF + 10 nF。", 9.2)

add_heading(doc, "2.3.10  电源监控", 3)
add_p(doc, "器件集成 POR/PDR，始终有效，保证从 2 V 起/降到 2 V 的正常工作。VDD 低于 VPOR/PDR 时器件保持复位，无需外部复位电路。")
add_p(doc, "PVD 可编程监测 VDD/VDDA，并与 VPVD 阈值比较；低于/高于阈值时可产生中断，中断服务程序可报警或让 MCU 进入安全状态。PVD 由软件使能，阈值见 5.3.3 节。")

add_heading(doc, "2.3.11  电压稳压器", 3)
add_p(doc, "内部稳压器有三种模式：主模式（MR，Run）、低功耗模式（LPR，Stop）和掉电模式（Standby）。Standby 时稳压器输出高阻，内核电路断电，寄存器/SRAM 内容丢失；复位后稳压器始终使能。")

add_heading(doc, "2.3.12  低功耗模式", 3)
add_p(doc, "器件支持 Sleep、Stop、Standby 三种低功耗模式，在功耗、启动时间和唤醒源之间折中。")
add_table(doc, ["模式", "CPU", "时钟", "SRAM/寄存器", "唤醒源"], [
    ["Sleep", "停止", "外设继续运行", "保持", "任意中断/事件"],
    ["Stop", "停止", "1.8 V 域时钟停止；PLL/HSI/HSE 关闭", "保持", "EXTI 线、PVD、RTC 闹钟、USB 唤醒"],
    ["Standby", "停止", "稳压器关闭，1.8 V 域断电", "丢失（备份域除外）", "NRST、IWDG、WKUP 上升沿、RTC 闹钟"],
], widths=[2.4, 2.2, 6.0, 3.4, 4.6], font_size=8.0)
add_p(doc, "注：RTC、IWDG 及其时钟源在 Stop/Standby 下不会停止。", 9.2)

add_heading(doc, "2.3.13  DMA", 3)
add_p(doc, "7 通道通用 DMA 支持存储器到存储器、外设到存储器、存储器到外设传输；支持循环缓冲，避免缓冲区结束中断。每个通道有专用硬件 DMA 请求，也支持软件触发。源/目标传输宽度可独立配置。DMA 可用于 SPI、I²C、USART、TIMx 和 ADC。")

add_heading(doc, "2.3.14  RTC 与备份寄存器", 3)
add_p(doc, "RTC 和备份寄存器通过开关供电：VDD 存在时用 VDD，否则用 VBAT。备份寄存器为 10 个 16 位寄存器，可在 VDD 掉电时保存 20 字节用户数据。")
add_p(doc, "RTC 提供连续计数器和闹钟/周期中断，可用 32.768 kHz 晶振、谐振器、内部 LSI 或 HSE/128 作为时钟。内部 LSI 典型 40 kHz。RTC 可用外部 512 Hz 输出校准；带 32 位可编程计数器、20 位预分频器，默认从 32.768 kHz 产生 1 秒时基。")

add_heading(doc, "2.3.15  定时器与看门狗", 3)
add_p(doc, "中密度器件包含 1 个高级控制定时器、3 个通用定时器、2 个看门狗和 1 个 SysTick。")
add_caption(doc, "表 4  定时器特性比较")
add_table(doc, ["定时器", "计数分辨率", "计数方向", "预分频", "DMA 请求", "捕获/比较通道", "互补输出"], [
    ["TIM1", "16 位", "上/下/上下", "1–65536 任意整数", "有", "4", "有"],
    ["TIM2/3/4", "16 位", "上/下/上下", "1–65536 任意整数", "有", "4", "无"],
], widths=[2.2, 2.2, 2.8, 3.6, 2.2, 2.6, 2.2], font_size=8.0)
add_p(doc, "TIM1 可视为 6 通道三相 PWM，带可编程死区和互补输出；4 个独立通道支持输入捕获、输出比较、PWM（边沿/中心对齐）、单脉冲。通用定时器 TIM2/3/4 为 16 位自动重装上/下计数器，带 16 位预分频和 4 个独立通道，支持输入捕获/输出比较/PWM/单脉冲，最多 12 路；支持正交编码器和霍尔传感器。")
add_p(doc, "独立看门狗 IWDG 基于 12 位递减计数器和 8 位预分频，时钟来自独立 40 kHz LSI，可在 Stop/Standby 运行，用于复位或应用超时。窗口看门狗 WWDG 基于 7 位递减计数器，时钟来自主时钟，带早期警告中断。两者都可在调试模式下冻结。")
add_p(doc, "SysTick 为 24 位递减计数器，带自动重装、可屏蔽系统中断、可编程时钟源，可用于 OS 或普通延时。")

add_heading(doc, "2.3.16  I²C 总线", 3)
add_p(doc, "最多 2 个 I²C 接口，支持多主/从模式、标准/快速模式、7 位双从地址、主模式 7/10 位寻址、硬件 CRC、DMA、SMBus 2.0/PMBus。")

add_heading(doc, "2.3.17  USART", 3)
add_p(doc, "一个 USART 最高 4.5 Mbit/s，其余最高 2.25 Mbit/s；支持 CTS/RTS 硬件流控、IrDA SIR ENDEC、ISO 7816、LIN 主/从；所有 USART 都可用 DMA。")

add_heading(doc, "2.3.18  SPI", 3)
add_p(doc, "最多 2 个 SPI，主/从模式最高 18 Mbit/s，支持全双工/单工、8/16 位帧、3 位预分频（8 种主模式频率）、硬件 CRC、SD 卡/MMC 基本模式、DMA。")

add_heading(doc, "2.3.19  CAN", 3)
add_p(doc, "CAN 符合 2.0A/B Active，最高 1 Mbit/s；支持 11 位标准帧和 29 位扩展帧；3 个发送邮箱、2 个 3 级接收 FIFO、14 个可扩展过滤器组。")

add_heading(doc, "2.3.20  USB", 3)
add_p(doc, "内嵌 USB 全速设备外设，兼容 USB 2.0 全速 12 Mbit/s；支持软件配置端点、挂起/恢复；48 MHz 时钟由主 PLL 产生，时钟源必须使用 HSE 晶振。")

add_heading(doc, "2.3.21  GPIO", 3)
add_p(doc, "每个 GPIO 可配置为推挽/开漏输出、带/不带上下拉输入、外设复用功能。大多数 GPIO 与数字/模拟复用功能共享。所有 GPIO 都具有较高驱动能力；复用功能配置可通过特定序列锁定，防止误写寄存器。APB2 上 I/O 最高翻转 18 MHz。")

add_heading(doc, "2.3.22  ADC", 3)
add_p(doc, "2 个 12 位 ADC，每个最多 16 个外部通道，支持单次/扫描、同时采样保持、交错采样、单分流；可用 DMA。模拟看门狗可监测一个/部分/全部通道，超出阈值产生中断。TIMx/TIM1 事件可内部连接到 ADC 启动/注入/DMA 触发，实现转换与定时器同步。")

add_heading(doc, "2.3.23  温度传感器", 3)
add_p(doc, "温度传感器输出电压随温度线性变化，转换范围 2 V < VDDA < 3.6 V；内部连接到 ADC12_IN16。")

add_heading(doc, "2.3.24  SWJ-DP 调试口", 3)
add_p(doc, "内嵌 Arm SWJ-DP，组合 JTAG 和 SWD；JTAG 的 TMS/TCK 与 SWDIO/SWCLK 复用，通过 TMS 上的特定序列在 JTAG-DP 与 SW-DP 之间切换。")

# ---------------- 3 Pinouts ----------------
add_heading(doc, "3  引脚定义  Pinouts and pin description", 1)
add_p(doc, "STM32F103x8/xB 提供多种封装：VFQFPN36、LQFP48、UFQFPN48、LQFP64、TFBGA64、LQFP100、LFBGA100、UFBGA100。不同封装的引脚数不同，但同一引脚在不同封装中的复用功能基本一致。")
add_p(doc, "本节以最常用的 LQFP48（7 mm × 7 mm，0.5 mm 间距）为例给出完整引脚表；其他封装请对照原版第 21–33 页的引脚图与表 5。")

add_heading(doc, "3.1  LQFP48 引脚表", 2)
add_p(doc, "类型列中：S = 电源；I = 输入；O = 输出；I/O = 通用输入/输出；FT = 5 V 容忍（5 V tolerant）。复用功能列只列常用功能，完整复用关系以原版表 5 和参考手册 AFIO 章节为准。")
rows = [
    ["1", "VBAT", "S", "VBAT", "RTC、备份寄存器、32 kHz 振荡器备用电源"],
    ["2", "PC13-TAMPER-RTC", "I/O", "PC13", "TAMPER-RTC；输出仅 ±3 mA"],
    ["3", "PC14-OSC32_IN", "I/O", "PC14", "OSC32_IN；输出仅 ±3 mA"],
    ["4", "PC15-OSC32_OUT", "I/O", "PC15", "OSC32_OUT；输出仅 ±3 mA"],
    ["5", "PD0-OSC_IN", "I", "OSC_IN", "PD0（重映射）；外部晶振输入"],
    ["6", "PD1-OSC_OUT", "O", "OSC_OUT", "PD1（重映射）；外部晶振输出"],
    ["7", "NRST", "I/O", "NRST", "复位，内部上拉"],
    ["8", "VSSA", "S", "VSSA", "模拟地"],
    ["9", "VDDA", "S", "VDDA", "模拟电源 2.0–3.6 V"],
    ["10", "PA0-WKUP", "I/O", "PA0", "TIM2_CH1、USART2_CTS、ADC12_IN0、WKUP"],
    ["11", "PA1", "I/O", "PA1", "TIM2_CH2、USART2_RTS、ADC12_IN1"],
    ["12", "PA2", "I/O", "PA2", "TIM2_CH3、USART2_TX、ADC12_IN2"],
    ["13", "PA3", "I/O", "PA3", "TIM2_CH4、USART2_RX、ADC12_IN3"],
    ["14", "PA4", "I/O", "PA4", "SPI1_NSS、USART2_CK、ADC12_IN4"],
    ["15", "PA5", "I/O", "PA5", "SPI1_SCK、ADC12_IN5"],
    ["16", "PA6", "I/O", "PA6", "SPI1_MISO、TIM3_CH1、ADC12_IN6"],
    ["17", "PA7", "I/O", "PA7", "SPI1_MOSI、TIM3_CH2、ADC12_IN7"],
    ["18", "PB0", "I/O", "PB0", "TIM3_CH3、ADC12_IN8"],
    ["19", "PB1", "I/O", "PB1", "TIM3_CH4、ADC12_IN9"],
    ["20", "PB2", "I/O FT", "PB2", "BOOT1"],
    ["21", "PB10", "I/O FT", "PB10", "I2C2_SCL、USART3_TX、TIM2_CH3"],
    ["22", "PB11", "I/O FT", "PB11", "I2C2_SDA、USART3_RX、TIM2_CH4"],
    ["23", "VSS_1", "S", "VSS_1", "数字地"],
    ["24", "VDD_1", "S", "VDD_1", "数字电源 2.0–3.6 V"],
    ["25", "PB12", "I/O FT", "PB12", "SPI2_NSS、I2C2_SMBAI、USART3_CK、TIM1_BKIN"],
    ["26", "PB13", "I/O FT", "PB13", "SPI2_SCK、USART3_CTS、TIM1_CH1N"],
    ["27", "PB14", "I/O FT", "PB14", "SPI2_MISO、USART3_RTS、TIM1_CH2N"],
    ["28", "PB15", "I/O FT", "PB15", "SPI2_MOSI、TIM1_CH3N"],
    ["29", "PA8", "I/O FT", "PA8", "USART1_CK、TIM1_CH1、MCO"],
    ["30", "PA9", "I/O FT", "PA9", "USART1_TX、TIM1_CH2"],
    ["31", "PA10", "I/O FT", "PA10", "USART1_RX、TIM1_CH3"],
    ["32", "PA11", "I/O FT", "PA11", "USART1_CTS、CAN_RX、USB_DM、TIM1_CH4"],
    ["33", "PA12", "I/O FT", "PA12", "USART1_RTS、CAN_TX、USB_DP、TIM1_ETR"],
    ["34", "PA13", "I/O FT", "PA13", "JTMS / SWDIO"],
    ["35", "VSS_2", "S", "VSS_2", "数字地"],
    ["36", "VDD_2", "S", "VDD_2", "数字电源"],
    ["37", "PA14", "I/O FT", "PA14", "JTCK / SWCLK"],
    ["38", "PA15", "I/O FT", "PA15", "JTDI、TIM2_CH1、SPI1_NSS"],
    ["39", "PB3", "I/O FT", "PB3", "JTDO、TIM2_CH2、SPI1_SCK"],
    ["40", "PB4", "I/O FT", "PB4", "NJTRST、TIM3_CH1、SPI1_MISO"],
    ["41", "PB5", "I/O FT", "PB5", "I2C1_SMBAI、TIM3_CH2、SPI1_MOSI"],
    ["42", "PB6", "I/O FT", "PB6", "I2C1_SCL、TIM4_CH1、USART1_TX（重映射）"],
    ["43", "PB7", "I/O FT", "PB7", "I2C1_SDA、TIM4_CH2、USART1_RX（重映射）"],
    ["44", "BOOT0", "I", "BOOT0", "启动模式选择，不能悬空"],
    ["45", "PB8", "I/O FT", "PB8", "TIM4_CH3、I2C1_SCL、CAN_RX（重映射）"],
    ["46", "PB9", "I/O FT", "PB9", "TIM4_CH4、I2C1_SDA、CAN_TX（重映射）"],
    ["47", "VSS_3", "S", "VSS_3", "数字地"],
    ["48", "VDD_3", "S", "VDD_3", "数字电源"],
]
add_caption(doc, "表 5（节选）  LQFP48 引脚定义")
add_table(doc, ["引脚", "名称", "类型", "复位后主功能", "常用复用功能 / 说明"], rows,
          widths=[1.2, 3.0, 1.7, 2.5, 8.6], font_size=7.8)

add_heading(doc, "3.2  引脚使用注意事项", 2)
add_bullet(doc, "所有 VDD、VSS、VDDA、VSSA 都必须连接；VDDA 与 VDD 建议同源，压差不超过 300 mV。")
add_bullet(doc, "PC13、PC14、PC15 只能输出 ±3 mA，输出速度不超过 2 MHz、负载不超过 30 pF；不适合直接驱动舵机、电机或大电流 LED。")
add_bullet(doc, "PA13、PA14 是 SWD 调试口（SWDIO/SWCLK），产品中保留，否则无法下载/调试。")
add_bullet(doc, "BOOT0 决定启动模式，必须通过电阻下拉或接明确电平，不能悬空。")
add_bullet(doc, "5 V 容忍（FT）引脚可以承受 5 V 输入，但前提是关闭内部上拉/下拉；模拟输入引脚不耐 5 V。")
add_bullet(doc, "复用功能不是“任意映射”：每个引脚可选功能由芯片固定，选引脚前先查表 5 / CubeMX。")

# ---------------- 4 Memory map ----------------
add_heading(doc, "4  存储器映射  Memory mapping", 1)
add_p(doc, "STM32F103x8/xB 采用统一的 32 位地址空间。Cortex®-M3 内核、Flash、SRAM、外设和系统存储区都映射到固定地址。表 4-1 给出常用区域；完整映射见原版图 11。")
add_caption(doc, "表 4-1  常用存储器与外设地址")
add_table(doc, ["区域", "起始地址", "结束地址", "说明"], [
    ["Flash（128 KB）", "0x0800 0000", "0x0801 FFFF", "64 KB 型号到 0x0800 FFFF"],
    ["SRAM（20 KB）", "0x2000 0000", "0x2000 4FFF", "CPU 零等待读写"],
    ["APB1 外设", "0x4000 0000", "0x4000 7FFF", "TIM2/3/4、I2C、USART、CAN 等"],
    ["APB2 外设", "0x4001 0000", "0x4001 3FFF", "GPIO、ADC、TIM1、SPI1、USART1 等"],
    ["AHB 外设", "0x4002 0000", "0x4002 3FFF", "DMA、RCC、Flash 接口"],
    ["USB/CAN 共享 SRAM", "0x4000 6000", "0x4000 61FF", "512 字节"],
    ["系统存储区", "0x1FFF F000", "0x1FFF F7FF", "Bootloader"],
    ["选项字节", "0x1FFF F800", "0x1FFF F80F", "读保护/写保护/复位选项"],
    ["Cortex-M3 内部", "0xE000 0000", "0xE00F FFFF", "NVIC、SysTick、SCB、MPU"],
], widths=[4.2, 3.2, 3.2, 7.4])
add_p(doc, "常用外设基地址：TIM2 0x4000 0000，TIM3 0x4000 0400，TIM4 0x4000 0800；I2C1 0x4000 5400，I2C2 0x4000 5800；USART1 0x4001 3800，USART2 0x4000 4400，USART3 0x4000 4800；SPI1 0x4001 3000，SPI2 0x4000 3800；CAN 0x4000 6400；GPIOA 0x4001 0800，GPIOB 0x4001 0C00，GPIOC 0x4001 1000；ADC1 0x4001 2400，ADC2 0x4001 2800；RCC 0x4002 1000，FLASH 接口 0x4002 2000。", 9.2)
add_note_box(doc, "对开发的直接意义", [
    "看参考手册时，外设寄存器地址 = 外设基地址 + 偏移。",
    "例如 GPIOA_ODR = 0x4001 0800 + 0x0C = 0x4001 080C。",
    "用 CubeMX/HAL 时不用手算，但调试查看内存/寄存器时需要这些地址。",
])

# ---------------- 5 Electrical ----------------
add_heading(doc, "5  电气特性  Electrical characteristics", 1)
add_p(doc, "除非另有说明，所有电压均以 VSS 为参考。最小/最大值是在环境温度、电源电压和频率最坏条件下，对 100% 产品做生产测试保证的；典型值是在 TA = 25 °C、VDD = 3.3 V 下的设计参考，不参与生产测试。")

add_heading(doc, "5.1  参数条件", 2)
add_p(doc, "数据手册中的“典型值”只用于设计参考；“最小/最大值”才是选型和保证的依据。基于表征、设计仿真或工艺特性的数据会在表脚注标明“未在生产中测试”。典型曲线不是保证值。")
add_p(doc, "引脚参数测量使用 50 pF 负载；引脚输入电压测量方式见原版图 12、图 13。")

add_heading(doc, "5.2  绝对最大额定值", 2)
add_p(doc, "超过表 6、表 7、表 8 的绝对最大额定值可能造成永久损坏。这些只是应力额定值，不代表器件在这些条件下可以正常工作；长时间处于极限条件会影响可靠性。")
add_caption(doc, "表 6  电压特性")
add_table(doc, ["符号", "参数", "最小", "最大", "单位"], [
    ["VDD – VSS", "外部主电源（含 VDDA、VDD）", "–0.3", "4.0", "V"],
    ["VIN（FT 引脚）", "5 V 容忍引脚输入电压", "VSS – 0.3", "VDD + 4.0", "V"],
    ["VIN（其他引脚）", "其他引脚输入电压", "VSS – 0.3", "4.0", "V"],
    ["|ΔVDDx|", "不同 VDD 电源引脚之间的偏差", "—", "50", "mV"],
    ["|VSSX – VSS|", "不同地引脚之间的偏差", "—", "50", "mV"],
], widths=[3.0, 7.2, 3.0, 3.0, 1.7])
add_caption(doc, "表 7  电流特性")
add_table(doc, ["符号", "参数", "最大", "单位"], [
    ["IVDD", "流入 VDD/VDDA 的总电流（源）", "150", "mA"],
    ["IVSS", "流出 VSS 的总电流（灌）", "150", "mA"],
    ["IIO", "任一 I/O 或控制引脚灌/拉电流", "±25", "mA"],
    ["IINJ(PIN)", "5 V 容忍引脚注入电流", "–5 / 0", "mA"],
    ["IINJ(PIN)", "其他引脚注入电流", "±5", "mA"],
    ["ΣIINJ(PIN)", "所有引脚注入电流绝对值之和", "±25", "mA"],
], widths=[3.0, 8.0, 3.5, 1.7])
add_caption(doc, "表 8  热特性")
add_table(doc, ["符号", "参数", "数值", "单位"], [
    ["TSTG", "存储温度", "–65 … +150", "°C"],
    ["TJ", "最大结温", "150", "°C"],
], widths=[3.0, 8.0, 3.5, 1.7])

add_heading(doc, "5.3  工作条件", 2)
add_heading(doc, "5.3.1  通用工作条件", 3)
add_caption(doc, "表 9  通用工作条件（节选）")
add_table(doc, ["符号", "参数", "条件", "最小", "最大", "单位"], [
    ["fHCLK", "内部 AHB 时钟", "—", "0", "72", "MHz"],
    ["fPCLK1", "APB1 时钟", "—", "0", "36", "MHz"],
    ["fPCLK2", "APB2 时钟", "—", "0", "72", "MHz"],
    ["VDD", "标准工作电压", "—", "2.0", "3.6", "V"],
    ["VDDA", "模拟工作电压（不用 ADC）", "与 VDD 同电位", "2.0", "3.6", "V"],
    ["VDDA", "模拟工作电压（用 ADC）", "—", "2.4", "3.6", "V"],
    ["VBAT", "备份工作电压", "—", "1.8", "3.6", "V"],
    ["VIN", "标准 I/O 输入电压", "—", "–0.3", "VDD+0.3", "V"],
    ["VIN", "FT I/O 输入电压", "2 V < VDD ≤ 3.6 V", "–0.3", "5.5", "V"],
    ["TA", "环境温度（6 后缀）", "最大功耗", "–40", "85", "°C"],
    ["TA", "环境温度（7 后缀）", "最大功耗", "–40", "105", "°C"],
    ["TJ", "结温（6/7 后缀）", "—", "–40", "105 / 125", "°C"],
], widths=[2.2, 5.2, 4.4, 1.9, 1.9, 1.5])
add_p(doc, "LQFP48 在 TA = 85 °C 时最大功耗为 363 mW；热阻 θJA = 55 °C/W。封装功耗与热设计详见第 6.2 节。", 9.2)

add_heading(doc, "5.3.2  上电/掉电条件", 3)
add_p(doc, "VDD 上升时间没有上限，下降时间不得快于 20 µs/V；上电/掉电过程应在通用工作条件范围内。")
add_heading(doc, "5.3.3  复位与电源控制", 3)
add_p(doc, "器件内置 POR/PDR，VDD 低于 VPOR/PDR 时保持复位，无需外部复位电路。PVD 可编程监测 VDD/VDDA，并产生中断。")
add_table(doc, ["参数", "条件", "最小", "典型", "最大", "单位"], [
    ["VPOR/PDR", "下降沿", "1.8", "1.88", "1.96", "V"],
    ["VPOR/PDR", "上升沿", "1.84", "1.92", "2.0", "V"],
    ["VPVD", "PLS[2:0]=000 上升沿", "2.10", "2.18", "2.26", "V"],
    ["VPVD", "PLS[2:0]=111 上升沿", "2.76", "2.88", "3.00", "V"],
    ["TRSTTEMPO", "复位延时", "1.0", "2.5", "4.5", "ms"],
], widths=[3.2, 5.2, 2.0, 2.0, 2.0, 1.5])
add_p(doc, "PVD 阈值共 8 档（PLS[2:0] = 000…111），每档有上升/下降沿两个值；上表只列首尾两档，完整表见原版表 11。", 9.2)

add_heading(doc, "5.3.4  内部参考电压", 3)
add_table(doc, ["符号", "参数", "条件", "最小", "典型", "最大", "单位"], [
    ["VREFINT", "内部参考电压", "–40…+105 °C", "1.16", "1.20", "1.26", "V"],
    ["VREFINT", "内部参考电压", "–40…+85 °C", "1.16", "1.20", "1.24", "V"],
    ["TS_vrefint", "读 VREFINT 的 ADC 采样时间", "—", "—", "5.1", "17.1", "µs"],
    ["TCoeff", "温度系数", "—", "—", "—", "100", "ppm/°C"],
], widths=[2.6, 4.8, 4.0, 1.6, 1.6, 1.6, 1.5])

add_heading(doc, "5.3.5  供电电流", 3)
add_p(doc, "电流消耗取决于工作电压、环境温度、I/O 负载、软件配置、工作频率、I/O 翻转率、程序存放位置和执行代码。以下数据是在所有 I/O 为输入、无负载、外设关闭（除非注明）条件下测得。")
add_caption(doc, "表 13/14  Run 模式最大 IDD（节选，TA = 85 °C）")
add_table(doc, ["fHCLK", "Flash 运行，全外设开", "Flash 运行，全外设关", "RAM 运行，全外设开", "RAM 运行，全外设关"], [
    ["72 MHz", "50.0 mA", "32.8 mA", "48 mA", "29 mA"],
    ["48 MHz", "36.1 mA", "24.4 mA", "31.5 mA", "20.5 mA"],
    ["36 MHz", "28.6 mA", "19.8 mA", "24 mA", "16 mA"],
    ["24 MHz", "19.9 mA", "13.9 mA", "17.5 mA", "11.5 mA"],
    ["16 MHz", "14.7 mA", "10.7 mA", "12.5 mA", "8.5 mA"],
    ["8 MHz", "8.6 mA", "6.8 mA", "7.5 mA", "5.5 mA"],
], widths=[2.4, 4.2, 4.2, 4.0, 4.0])
add_p(doc, "Sleep 模式：72 MHz 全外设开约 30 mA，全外设关约 7.5 mA；8 MHz 全外设开约 5.5 mA，关约 3 mA。Stop 模式典型 13.5–24 µA（稳压器低功耗/运行模式不同），Standby 模式典型 1.7–3.4 µA。", 9.2)
add_p(doc, "外设电流（µA/MHz）：TIM2 32.50、TIM3 31.39、TIM4 31.94、I2C1/2 10.00、USART1 11.94、USART2/3 12.22、SPI1 4.72、SPI2 4.17、CAN1 18.06、USB 17.78、ADC1 17.50、ADC2 16.07。", 9.2)
add_caption(doc, "表 15/16  Sleep、Stop、Standby 电流（节选）")
add_table(doc, ["模式", "条件", "典型", "最大", "单位"], [
    ["Sleep，72 MHz", "全外设开 / 全外设关", "30 / 7.5", "32 / 8", "mA"],
    ["Sleep，8 MHz", "全外设开 / 全外设关", "5.5 / 3", "6 / 4", "mA"],
    ["Stop，稳压器 Run", "LSI/HSI/HSE 关，无 IWDG", "23.5 µA（2.4 V）", "370 µA（105 °C）", "µA"],
    ["Stop，稳压器 LPR", "LSI/HSI/HSE 关，无 IWDG", "13.5 µA（2.4 V）", "340 µA（105 °C）", "µA"],
    ["Standby", "LSI + IWDG 开", "2.6 µA（2.0 V）", "—", "µA"],
    ["Standby", "LSI 开，IWDG 关", "2.4 µA（2.0 V）", "—", "µA"],
    ["Standby", "LSI/IWDG/RTC 全关", "1.7 µA（2.0 V）", "5 µA（105 °C）", "µA"],
    ["VBAT 备份域", "LSE + RTC 开", "0.9 µA（2.0 V）", "2.2 µA（105 °C）", "µA"],
], widths=[4.2, 6.0, 3.2, 3.2, 1.5])

add_heading(doc, "5.3.6  外部时钟", 3)
add_p(doc, "HSE 外部用户时钟：1–25 MHz，OSC_IN 高电平 ≥ 0.7VDD、低电平 ≤ 0.3VDD，占空比 45–55%，上升/下降时间 ≤ 20 ns。HSE 晶振/陶瓷谐振器：4–16 MHz，典型 8 MHz，启动时间约 2 ms。")
add_p(doc, "LSE 外部用户时钟：32.768 kHz（最大 1000 kHz），占空比 30–70%；LSE 晶振 32.768 kHz，启动时间随温度变化（25 °C 约 2.5 s，–40 °C 约 60 s）。")
add_p(doc, "晶振负载电容 CL = CL1 × CL2 / (CL1 + CL2) + Cstray；Cstray 通常 2–7 pF。LSE 建议使用 CL ≤ 7 pF 的谐振器，CL1/CL2 最大 15 pF。", 9.2)
add_caption(doc, "表 20/21  外部时钟源特性（节选）")
add_table(doc, ["参数", "条件", "最小", "典型", "最大", "单位"], [
    ["HSE 外部时钟频率", "—", "1", "8", "25", "MHz"],
    ["HSE 高/低电平", "OSC_IN", "0.7VDD / VSS", "—", "VDD / 0.3VDD", "V"],
    ["HSE 占空比", "—", "45", "—", "55", "%"],
    ["HSE 晶振频率", "—", "4", "8", "16", "MHz"],
    ["HSE 启动时间", "VDD 稳定后", "—", "2", "—", "ms"],
    ["LSE 外部时钟频率", "—", "—", "32.768", "1000", "kHz"],
    ["LSE 占空比", "—", "30", "—", "70", "%"],
    ["LSE 启动时间", "25 °C / –40 °C", "—", "2.5 / 60", "—", "s"],
], widths=[4.2, 5.4, 2.2, 2.2, 2.2, 1.5])

add_heading(doc, "5.3.7  内部时钟", 3)
add_table(doc, ["时钟", "频率", "精度/备注"], [
    ["HSI", "8 MHz", "出厂校准；–40…105 °C 约 –2%…+2.5%；25 °C 约 –1.1%…+1.8%"],
    ["LSI", "30/40/60 kHz（典型 40 kHz）", "独立看门狗时钟；启动 ≤ 85 µs"],
    ["LSE", "32.768 kHz", "RTC 时钟；需外部晶振"],
    ["HSE", "4–16 MHz", "外部晶振/陶瓷谐振器"],
], widths=[2.4, 5.4, 9.0])
add_p(doc, "低功耗唤醒时间：Sleep 约 1.8 µs；Stop（稳压器运行/低功耗）约 3.6/5.4 µs；Standby 约 50 µs。PLL 锁定时间 ≤ 200 µs，周期抖动 ≤ 300 ps。", 9.2)
add_caption(doc, "表 24/25  内部时钟源特性")
add_table(doc, ["时钟", "参数", "最小", "典型", "最大", "单位"], [
    ["HSI", "频率", "—", "8", "—", "MHz"],
    ["HSI", "占空比", "45", "—", "55", "%"],
    ["HSI", "出厂校准精度（–40…105 °C）", "–2%", "—", "+2.5%", "—"],
    ["HSI", "25 °C 精度", "–1.1%", "—", "+1.8%", "—"],
    ["HSI", "启动时间", "—", "1", "2", "µs"],
    ["HSI", "功耗", "—", "80", "100", "µA"],
    ["LSI", "频率", "30", "40", "60", "kHz"],
    ["LSI", "启动时间", "—", "—", "85", "µs"],
    ["LSI", "功耗", "—", "0.65", "1.2", "µA"],
], widths=[2.2, 6.0, 2.4, 2.4, 2.4, 1.5])

add_heading(doc, "5.3.8  PLL", 3)
add_table(doc, ["参数", "最小", "典型", "最大", "单位"], [
    ["PLL 输入时钟", "1", "8.0", "25", "MHz"],
    ["PLL 输入占空比", "40", "—", "60", "%"],
    ["PLL 输出时钟", "16", "—", "72", "MHz"],
    ["锁定时间", "—", "—", "200", "µs"],
    ["周期抖动", "—", "—", "300", "ps"],
], widths=[6.0, 2.8, 2.8, 2.8, 2.0])

add_heading(doc, "5.3.9  存储器特性", 3)
add_table(doc, ["参数", "条件", "最小", "典型", "最大", "单位"], [
    ["16 位编程时间", "TA = –40…+105 °C", "40", "52.5", "70", "µs"],
    ["页（1 KB）擦除时间", "TA = –40…+105 °C", "20", "—", "40", "ms"],
    ["全片擦除时间", "TA = –40…+105 °C", "20", "—", "40", "ms"],
    ["编程电压", "—", "2.0", "—", "3.6", "V"],
    ["擦写次数", "TA = –40…+85 °C", "10k", "—", "—", "次"],
    ["数据保持", "1k 次擦写，85 °C", "30", "—", "—", "年"],
    ["数据保持", "1k 次擦写，105 °C", "10", "—", "—", "年"],
], widths=[4.0, 5.2, 1.8, 1.8, 1.8, 1.5])

add_heading(doc, "5.3.10  EMC 特性", 3)
add_p(doc, "EMS 测试按 IEC 61000-4-2（ESD）和 IEC 61000-4-4（快速瞬变脉冲群）进行；测试时器件运行简单程序（翻转 2 个 LED），直到出现功能扰动。ESD 测试对全部引脚施加正/负放电；FTB 通过 100 pF 电容对 VDD/VSS 施加正/负脉冲。复位后器件恢复正常。")
add_p(doc, "EMI 测试按 IEC 61967-2 进行，具体等级见原版表 30、表 31。")
add_caption(doc, "表 30/31  EMS / EMI 特性（节选）")
add_table(doc, ["项目", "条件", "等级/数值"], [
    ["EMS：ESD 功能扰动", "IEC 61000-4-2，3.3 V，25 °C，72 MHz", "2B"],
    ["EMS：快速瞬变脉冲群", "IEC 61000-4-4，100 pF 耦合到 VDD/VSS", "4A"],
    ["EMI：0.1–30 MHz", "IEC 61967-2，LQFP100", "12 dBµV"],
    ["EMI：30–130 MHz", "同上", "22 / 19 dBµV（8/48、8/72 MHz）"],
    ["EMI：130 MHz–1 GHz", "同上", "23 / 29 dBµV"],
    ["EMI 等级", "SAE", "4"],
], widths=[4.0, 8.0, 4.0])

add_heading(doc, "5.3.11  ESD 与电气敏感性", 3)
add_p(doc, "ESD 绝对最大额定值：HBM 2 kV，CDM 500 V（具体以原版表 32 为准）。器件为敏感器件，拿取、焊接、测试时必须做防静电措施。")
add_p(doc, "静态闩锁（latch-up）测试按 JESD78 进行；具体等级见原版表 33。")
add_caption(doc, "表 32/33  ESD 与闩锁特性")
add_table(doc, ["符号", "参数", "条件", "等级", "数值"], [
    ["VESD(HBM)", "人体模型 ESD", "JESD22-A114，25 °C", "2", "2000 V"],
    ["VESD(CDM)", "器件充电模型 ESD", "ANSI/ESD STM5.3.1，25 °C", "II", "500 V"],
    ["LU", "静态闩锁", "JESD78A，105 °C", "II level A", "—"],
], widths=[3.0, 5.0, 6.0, 2.0, 2.5])

add_heading(doc, "5.3.12  I/O 电流注入", 3)
add_p(doc, "5 V 容忍引脚不允许正向注入（VIN > VDD），负向注入最大 –5 mA；其他引脚正/负注入最大 ±5 mA；所有引脚注入电流绝对值之和不超过 ±25 mA。负向注入会干扰模拟性能，模拟输入脚建议加肖特基二极管到地。")

add_heading(doc, "5.3.13  I/O 端口特性", 3)
add_p(doc, "所有 I/O 兼容 CMOS 和 TTL。标准 I/O 的 VIL/VIH 与 VDD 有关；FT 引脚可承受 5 V，但前提是关闭内部上拉/下拉。")
add_table(doc, ["参数", "条件", "最小", "最大", "单位"], [
    ["VIL（标准 I/O）", "—", "—", "0.28×(VDD–2)+0.8", "V"],
    ["VIH（标准 I/O）", "—", "0.41×(VDD–2)+1.3", "—", "V"],
    ["VIL（FT I/O）", "—", "—", "0.32×(VDD–2)+0.75", "V"],
    ["VIH（FT I/O）", "—", "0.42×(VDD–2)+1.0", "—", "V"],
    ["Vhys（标准）", "施密特迟滞", "—", "200", "mV"],
    ["Vhys（FT）", "施密特迟滞", "—", "5%VDD（最小 100）", "mV"],
    ["RPU/RPD", "弱上拉/下拉", "30", "50", "kΩ"],
    ["CIO", "引脚电容", "—", "5", "pF"],
], widths=[4.0, 4.0, 4.0, 4.0, 1.8])
add_p(doc, "GPIO 可灌/拉 ±8 mA；在放宽 VOL/VOH 时可到 ±20 mA。PC13、PC14、PC15 只能 ±3 mA，输出速度 ≤ 2 MHz、负载 ≤ 30 pF。所有 I/O 电流之和不能超过 IVDD/IVSS 的 150 mA 绝对最大值。", 9.2)
add_p(doc, "输出电平（8 引脚同时 8 mA）：VOL ≤ 0.4 V，VOH ≥ VDD–0.4 V；20 mA 时 VOL ≤ 1.3 V，VOH ≥ VDD–1.3 V。I/O 速度模式 10/01/11 对应最大 2/10/50 MHz。", 9.2)

add_heading(doc, "5.3.14  NRST 引脚", 3)
add_table(doc, ["参数", "条件", "最小", "典型", "最大", "单位"], [
    ["VIL(NRST)", "—", "–0.5", "—", "0.8", "V"],
    ["VIH(NRST)", "—", "2.0", "—", "VDD+0.5", "V"],
    ["Vhys(NRST)", "—", "—", "200", "—", "mV"],
    ["RPU", "VIN = VSS", "30", "40", "50", "kΩ"],
    ["VF(NRST)", "输入滤波脉冲", "—", "—", "100", "ns"],
    ["VNF(NRST)", "不滤波脉冲", "300", "—", "—", "ns"],
], widths=[3.2, 4.8, 2.4, 2.4, 2.4, 1.6])
add_p(doc, "NRST 内部有约 40 kΩ 上拉，建议外部 0.1 µF 电容到地；外部复位电路必须能把 NRST 拉到 VIL(NRST) 以下，否则不会触发复位。", 9.2)

add_heading(doc, "5.3.15  TIM 定时器", 3)
add_table(doc, ["参数", "条件", "最小", "最大", "单位"], [
    ["定时器分辨率", "—", "—", "16", "bit"],
    ["计数时钟周期", "fTIMxCLK = 72 MHz", "13.9", "—", "ns"],
    ["外部时钟频率", "CH1–CH4", "0", "fTIMxCLK/2", "MHz"],
    ["16 位计数周期", "fTIMxCLK = 72 MHz", "0.0139", "910", "µs"],
    ["最大计数时间", "fTIMxCLK = 72 MHz", "—", "59.6", "s"],
], widths=[4.5, 5.5, 2.5, 2.8, 1.8])

add_heading(doc, "5.3.16  通信接口", 3)
add_heading(doc, "I²C", 4) if False else add_p(doc, "I²C：支持标准模式（100 kHz）和快速模式（400 kHz），7/10 位寻址，硬件 CRC，SMBus 2.0/PMBus。SDA/SCL 不是“真”开漏，配置为开漏时 PMOS 仍存在但关闭。标准模式 SCL 低/高 ≥ 4.7/4.0 µs；快速模式 ≥ 1.3/0.6 µs；总线电容 ≤ 400 pF。")
add_p(doc, "SPI：主机/从机最高 18 Mbit/s，支持 8/16 位帧、硬件 CRC、DMA；SPI1 在 APB2（72 MHz），SPI2 在 APB1（36 MHz）。")
add_p(doc, "USART：USART1 最高 4.5 Mbit/s，USART2/3 最高 2.25 Mbit/s；支持 CTS/RTS、IrDA、ISO 7816、LIN。")
add_p(doc, "USB：全速 12 Mbit/s，USB 2.0 全速设备；USBDP（D+）需 1.5 kΩ 上拉到 3.0–3.6 V；USB 工作电压 3.0–3.6 V。")
add_p(doc, "CAN：2.0A/B Active，最高 1 Mbit/s；3 个发送邮箱、2 个接收 FIFO（每 FIFO 3 级）、14 个可扩展过滤器组；支持 11 位标准帧和 29 位扩展帧。", 10.2)
add_caption(doc, "表 40/42  I²C 与 SPI 关键参数（节选）")
add_table(doc, ["接口", "参数", "标准/主机", "快速/从机", "单位"], [
    ["I²C", "SCL 低电平时间", "≥ 4.7", "≥ 1.3", "µs"],
    ["I²C", "SCL 高电平时间", "≥ 4.0", "≥ 0.6", "µs"],
    ["I²C", "SDA 建立时间", "≥ 250", "≥ 100", "ns"],
    ["I²C", "总线电容", "≤ 400", "≤ 400", "pF"],
    ["SPI", "SCK 频率（主/从）", "≤ 18", "≤ 18", "MHz"],
    ["SPI", "SCK 上升/下降时间", "≤ 8", "≤ 8", "ns"],
    ["SPI", "从机时钟占空比", "30–70", "30–70", "%"],
], widths=[2.2, 6.2, 4.2, 4.2, 1.5])

add_heading(doc, "5.3.17  CAN 接口", 3)
add_p(doc, "CAN_TX/CAN_RX 的电气特性参见 I/O 端口特性。STM32F103 的 CAN 控制器需要外部收发器（如 TJA1050、SN65HVD230）才能形成差分 CAN_H/CAN_L；总线两端各 120 Ω 终端电阻，所有节点共地。")

add_heading(doc, "5.3.18  12 位 ADC", 3)
add_table(doc, ["参数", "条件", "最小", "典型", "最大", "单位"], [
    ["VDDA", "电源", "2.4", "—", "3.6", "V"],
    ["VREF+", "正参考", "2.4", "—", "VDDA", "V"],
    ["fADC", "ADC 时钟", "0.6", "—", "14", "MHz"],
    ["采样率", "—", "0.05", "—", "1", "Msps"],
    ["外部输入阻抗 RAIN", "—", "—", "—", "50", "kΩ"],
    ["采样保持电容 CADC", "—", "—", "—", "8", "pF"],
    ["校准时间", "fADC = 14 MHz", "5.9", "—", "—", "µs"],
    ["总转换时间", "fADC = 14 MHz", "1", "—", "18", "µs"],
    ["总未调整误差 ET", "25 °C，校准后", "—", "±1.3", "±2", "LSB"],
    ["总未调整误差 ET", "全温度范围", "—", "±2", "±5", "LSB"],
], widths=[4.2, 5.0, 2.2, 2.2, 2.2, 1.5])
add_p(doc, "12 位 ADC 共 16 个外部通道（具体可用通道随封装变化）；支持单次/扫描、双采样保持、交错采样、模拟看门狗、DMA。每次上电后建议执行一次校准。", 9.2)
add_caption(doc, "表 48/49  ADC 精度（节选）")
add_table(doc, ["参数", "测试条件", "典型", "最大", "单位"], [
    ["总未调整误差 ET", "25 °C，校准后", "±1.3", "±2", "LSB"],
    ["偏移误差 EO", "25 °C，校准后", "±1.0", "±1.5", "LSB"],
    ["增益误差 EG", "25 °C，校准后", "±0.5", "±1.5", "LSB"],
    ["微分线性误差 ED", "25 °C，校准后", "±0.7", "±1.0", "LSB"],
    ["积分线性误差 EL", "25 °C，校准后", "±0.8", "±1.5", "LSB"],
    ["总未调整误差 ET", "全温度范围", "±2", "±5", "LSB"],
], widths=[4.4, 6.2, 2.6, 2.6, 1.5])
add_p(doc, "最大外部输入阻抗 RAIN 与采样时间有关：fADC = 14 MHz、采样 1.5 周期时约 0.4 kΩ；7.5 周期约 5.9 kΩ；13.5 周期约 11.4 kΩ；28.5 周期约 25.2 kΩ；41.5 周期约 37.2 kΩ；55.5 周期约 50 kΩ。采样时间越长，允许的源阻抗越大。", 9.2)

add_heading(doc, "5.3.19  温度传感器", 3)
add_table(doc, ["参数", "最小", "典型", "最大", "单位"], [
    ["VSENSE 线性度", "—", "±1", "±2", "°C"],
    ["平均斜率", "4.0", "4.3", "4.6", "mV/°C"],
    ["25 °C 时电压 V25", "1.34", "1.43", "1.52", "V"],
    ["启动时间", "4", "—", "10", "µs"],
], widths=[5.0, 3.0, 3.0, 3.0, 2.0])
add_p(doc, "温度传感器内部连接到 ADC12_IN16；转换范围 2 V < VDDA < 3.6 V。", 9.2)

# ---------------- 6 Package ----------------
add_heading(doc, "6  封装信息  Package information", 1)
add_p(doc, "为满足环保要求，ST 提供不同等级 ECOPACK® 封装；具体等级和产品状态见 www.st.com。ECOPACK® 是 ST 的商标。")
add_p(doc, "本系列封装包括：VFQFPN36、LQFP48、UFQFPN48、LQFP64、TFBGA64、LQFP100、LFBGA100、UFBGA100。")
add_caption(doc, "表 6-1  封装概览")
add_table(doc, ["封装", "引脚数", "本体尺寸", "引脚间距", "θJA（°C/W）"], [
    ["VFQFPN36", "36", "6 × 6 mm", "0.5 mm", "18"],
    ["LQFP48", "48", "7 × 7 mm", "0.5 mm", "55"],
    ["UFQFPN48", "48", "7 × 7 mm", "0.5 mm", "32"],
    ["LQFP64", "64", "10 × 10 mm", "0.5 mm", "45"],
    ["TFBGA64", "64", "5 × 5 mm", "0.5 mm", "65"],
    ["LQFP100", "100", "14 × 14 mm", "0.5 mm", "46"],
    ["LFBGA100", "100", "10 × 10 mm", "0.8 mm", "44"],
    ["UFBGA100", "100", "7 × 7 mm", "0.5 mm", "59"],
], widths=[3.4, 2.2, 4.0, 3.0, 3.4])
add_heading(doc, "6.1  LQFP48 封装", 2)
add_p(doc, "LQFP48 为 48 引脚、7 mm × 7 mm、0.5 mm 引脚间距的低-profile 四方扁平封装，本体厚度典型 1.4 mm。")
add_caption(doc, "表 61（节选）  LQFP48 机械尺寸")
add_table(doc, ["符号", "最小（mm）", "典型（mm）", "最大（mm）"], [
    ["A", "—", "—", "1.600"],
    ["A1", "0.050", "—", "0.150"],
    ["A2", "1.350", "1.400", "1.450"],
    ["b", "0.170", "0.220", "0.270"],
    ["c", "0.090", "—", "0.200"],
    ["D", "8.800", "9.000", "9.200"],
    ["D1", "6.800", "7.000", "7.200"],
    ["E", "8.800", "9.000", "9.200"],
    ["E1", "6.800", "7.000", "7.200"],
    ["e", "—", "0.500", "—"],
    ["L", "0.450", "0.600", "0.750"],
    ["L1", "—", "1.000", "—"],
    ["k", "0°", "3.5°", "7°"],
], widths=[2.0, 4.0, 4.0, 4.0])
add_p(doc, "完整封装图、推荐焊盘和公差请查原版第 101–103 页图 62、图 63、图 64。", 9.2)
add_heading(doc, "6.2  热特性", 2)
add_p(doc, "最大结温 TJmax 不得超过表 9 给出的值。计算公式：TJmax = TAmax + (PDmax × θJA)，其中 PDmax = PINTmax + PI/O max。")
add_table(doc, ["封装", "θJA（°C/W）"], [
    ["LQFP48（7×7 mm，0.5 mm）", "55"],
    ["UFQFPN48（7×7 mm）", "32"],
    ["LQFP64（10×10 mm）", "45"],
    ["LQFP100（14×14 mm）", "46"],
    ["TFBGA64（5×5 mm）", "65"],
    ["VFQFPN36（6×6 mm）", "18"],
], widths=[8.0, 4.0])
add_p(doc, "LQFP48 在 85 °C 环境、363 mW 功耗下，TJ = 85 + 55 × 0.363 ≈ 105 °C，接近 6 后缀上限；高功耗设计要留余量。", 9.2)

# ---------------- 7 Ordering ----------------
add_heading(doc, "7  订购信息  Ordering information scheme", 1)
add_p(doc, "订购代码格式：STM32 F103 C 8 T 6 xxx。")
add_table(doc, ["字段", "含义", "取值"], [
    ["STM32", "基于 Arm 的 32 位 MCU", "STM32"],
    ["F", "通用产品类型", "F = 通用"],
    ["103", "性能系列子家族", "103"],
    ["C", "引脚数", "T=36，C=48，R=64，V=100"],
    ["8 / B", "Flash 容量", "8=64 KB，B=128 KB"],
    ["T", "封装", "H=BGA，I=UFBGA，T=LQFP，U=VFQFPN/UFQFPN"],
    ["6 / 7", "温度范围", "6=–40…+85 °C，7=–40…+105 °C"],
    ["xxx", "选项", "xxx=编程件，TR=编带"],
], widths=[2.4, 5.2, 9.0])
add_p(doc, "例：STM32F103C8T6 = 48 引脚 LQFP、64 KB Flash、–40…+85 °C；STM32F103CBT6 = 48 引脚 LQFP、128 KB Flash、–40…+85 °C。", 9.5)

# ---------------- 8 Revision ----------------
add_heading(doc, "8  版本历史  Revision history", 1)
add_p(doc, "本翻译版依据 DS5319 Rev 18（2022 年 3 月）。原版版本历史从 2007 年 Rev 1 开始，历经多次引脚表、电气参数、封装图和注释修订；Rev 18 为当前版本。")
add_p(doc, "版本历史中的具体修改项（如 Rev 2 增加 BGA100 引脚、修改 VBAT 范围、修正 tSU(LSE)、增加 IDD(HSI) 最大值等）请查原版表 63。做正式设计时，应以订单对应的最新英文版为准。")

# ---------------- Appendix ----------------
add_heading(doc, "附录 A  术语表", 1)
add_table(doc, ["缩写", "英文", "中文/说明"], [
    ["MCU", "Microcontroller Unit", "微控制器"],
    ["CPU", "Central Processing Unit", "中央处理器"],
    ["Flash", "Flash memory", "闪存，存程序/常量"],
    ["SRAM", "Static Random Access Memory", "静态随机存储器，存变量/栈"],
    ["GPIO", "General-Purpose Input/Output", "通用输入/输出"],
    ["AF", "Alternate Function", "复用功能"],
    ["NVIC", "Nested Vectored Interrupt Controller", "嵌套向量中断控制器"],
    ["EXTI", "External Interrupt/Event Controller", "外部中断/事件控制器"],
    ["DMA", "Direct Memory Access", "直接存储器访问"],
    ["RTC", "Real-Time Clock", "实时时钟"],
    ["IWDG/WWDG", "Independent/Window Watchdog", "独立/窗口看门狗"],
    ["TIM", "Timer", "定时器"],
    ["ADC", "Analog-to-Digital Converter", "模数转换器"],
    ["PWM", "Pulse Width Modulation", "脉冲宽度调制"],
    ["USART", "Universal Synchronous/Asynchronous Receiver Transmitter", "通用同步/异步收发器"],
    ["SPI", "Serial Peripheral Interface", "串行外设接口"],
    ["I²C", "Inter-Integrated Circuit", "内部集成电路总线"],
    ["CAN", "Controller Area Network", "控制器局域网"],
    ["USB", "Universal Serial Bus", "通用串行总线"],
    ["SWD", "Serial Wire Debug", "串行线调试"],
    ["JTAG", "Joint Test Action Group", "联合测试行动组调试接口"],
    ["POR/PDR", "Power-On/Power-Down Reset", "上电/掉电复位"],
    ["PVD", "Programmable Voltage Detector", "可编程电压检测器"],
    ["HSE/HSI", "High-Speed External/Internal clock", "高速外部/内部时钟"],
    ["LSE/LSI", "Low-Speed External/Internal clock", "低速外部/内部时钟"],
    ["PLL", "Phase-Locked Loop", "锁相环"],
    ["LSB", "Least Significant Bit", "最低有效位"],
    ["ESD", "Electrostatic Discharge", "静电放电"],
    ["EMC", "Electromagnetic Compatibility", "电磁兼容"],
], widths=[2.2, 8.2, 6.0], font_size=8.0)

add_heading(doc, "附录 B  使用提醒", 1)
add_bullet(doc, "本翻译版对原文进行了技术性意译，省略了部分重复的法律声明、包装图和曲线图；关键参数以表格形式保留。")
add_bullet(doc, "电气参数请以原版 DS5319 Rev 18 的表格和脚注为准，尤其是“典型值”不是保证值。")
add_bullet(doc, "引脚复用、寄存器定义、启动流程以 STM32F10xxx 参考手册（RM0008）为准。")
add_bullet(doc, "做 PCB 前，请用原版封装图核对焊盘尺寸；本翻译版只给出 LQFP48 的主要机械尺寸。")
add_bullet(doc, "若用于功能安全、汽车、医疗等场景，请获取 ST 官方最新英文版并遵循其认证要求。")

doc.save(OUT / "STM32F103x8_xB_数据手册_中文翻译版.docx")
print("saved", OUT / "STM32F103x8_xB_数据手册_中文翻译版.docx")
