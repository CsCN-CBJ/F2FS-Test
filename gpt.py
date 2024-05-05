import time
from cbjLibrary.gpt import GPTClient

ENCODING = "utf-8"
gpt = GPTClient()


def polish(content: str):
    """
    修改论文片段
    :param content: 原始论文片段
    :return: 修改后的论文片段
    """
    prompt = f"""You are now acting as an expert in the field of writing SCI academic papers.
    Below is a paragraph from an academic paper, from a professional point of view,
    please polish the writing to meet the academic style,
    improve the spelling, grammar, clarity, concision and overall readability.
    Be careful not to modify the full text or add any new content, just modify the original sentence.
    The paragraph is written in LaTeX format, so you should not modify the format,
    for example: you should ignore content surrounded with pairs of `$`.
    You should just reply with the modified paragraph, without any other content.
    The content as follows: 
    ```{content}```
    """
    return gpt.gpt_35_api(prompt)


def polishChinese(content: str):
    """
    修改论文片段
    :param content: 原始论文片段
    :return: 修改后的论文片段
    """
    prompt = f"""您现在是计算机系统领域中文学术论文领域的专家，我希望你将我的中文论文进行润色。
    以下是我的论文中的一段话，请你从专业的角度，来润色文笔，以符合中文学术风格，提高语句的语法、通顺程度、清晰程度、准确程度和整体的可读性。
    注意不要修改全文或添加任何新内容，只需修改原句即可。
    该段落是用 LaTeX 格式编写的，因此您不应该修改格式，例如：您应该忽略用“$”对包围的内容。
    您应该只回复修改后的中文段落，而不用任何其他内容。
    内容如下：
    ```{content}```
    """
    return gpt.gpt_35_api(prompt)


def filterLines(lines: list[str]):
    """
    过滤掉不需要的行
    """
    newLines = []
    begin = False
    for line in lines:
        line = line.strip()

        # 需要配对的行
        passBeginEnd = ['table', 'figure', 'equation']
        if line.startswith(tuple(map(lambda x: r"\end{" + x + "}", passBeginEnd))):
            begin = False
            continue

        # 需要配对的行
        if line.startswith(tuple(map(lambda x: r"\begin{" + x + "}", passBeginEnd))):
            begin = True
            continue

        # 直接跳过的行
        passDirectly = ('%', r'\chapter', r'\section', r'\subsection', r'\subsubsection', r'\caption{', r'\centerline{',
                        r'\begin{', r'\end{')
        if begin or line.startswith(passDirectly) or line == '':
            continue

        newLines.append(line)

    return newLines


def readAndPolish(fileBaseName, send=False):
    """
    读取论文并修改, 建议每次与GPT对话之前, 先将return取消注释, 查看输出的文件是否正确
    """
    src = f"./paper/{fileBaseName}.txt"
    dst1 = f"./paper/{fileBaseName}_1.txt"
    dst2 = f"./paper/{fileBaseName}_2.txt"
    lines = []
    with open(src, "r", encoding=ENCODING) as f:
        for line in f:
            lines.append(line)
    lines = filterLines(lines)  # lines没有换行符

    with open(dst1, "w", encoding=ENCODING) as f:
        for line in lines:
            f.write(line + '\n\n')
    if not send:
        print(f"please check {fileBaseName}_1.txt.")
        return

    newLines = []
    with open(dst2, "w", encoding=ENCODING) as f:
        for idx, line in enumerate(lines):
            print(idx)
            try:
                newLine = polishChinese(line)
                time.sleep(1)
                if not newLine.endswith('\n'):
                    newLine += '\n\n'
                newLines.append(newLine)
            except Exception as e:
                print(e)
                print(f"Error at line {idx}")
                f.writelines(newLines)
                break
        f.writelines(newLines)

    print(f"Polish {fileBaseName} done.")


def main():
    readAndPolish("abstract")
    # readAndPolish("motivation", send=True)
    # readAndPolish("introduction")
    # readAndPolish("bg")
    # readAndPolish("design")
    # readAndPolish("evaluation")
    # readAndPolish("eva1")
    # readAndPolish("eva2")
    # readAndPolish("conclusion")


if __name__ == '__main__':
    main()
