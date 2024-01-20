import time
from cbjLibrary.gpt import gpt_35_api

ENCODING = "utf-8"


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
    return gpt_35_api(prompt)


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
        passDirectly = ('%', r'\section', r'\subsection', r'\subsubsection', r'\caption{', r'\centerline{',
                        r'\begin{', r'\end{')
        if begin or line.startswith(passDirectly) or line == '':
            continue

        newLines.append(line)

    return newLines


def readAndPolish(fileBaseName):
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

    # return
    newLines = []
    with open(dst2, "w", encoding=ENCODING) as f:
        for idx, line in enumerate(lines):
            print(idx)
            try:
                newLine = polish(line)
                # time.sleep(60)
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
    # readAndPolish("introduction")
    # readAndPolish("bg")
    # readAndPolish("design")
    # readAndPolish("evaluation")
    # readAndPolish("eva1")
    # readAndPolish("eva2")
    # readAndPolish("conclusion")


if __name__ == '__main__':
    main()
