
def add_bold(paragraph, text):
    added= paragraph.add_run(text)
    added.bold=True

def sections(paragraph_name, count):
    paragraph_prep =paragraph_name.replace(" ", "_")
    p_paragraph = f"p_{paragraph_prep}"
    p_paragraph = report.add_paragraph(f"{paragraph_name} Count: ")
    add_bold(p_paragraph, f"{count}")

def explanations(paragraph_name, text):

    p_paragraph = f"p_example_{paragraph_name}"
    p_paragraph = report.add_paragraph(f"\t{num} - ")


    add_bold(p_paragraph, f"{text}")


report = docx.Document()
sections("Title Page", test.title_count)
sections("Figures", test.figures_count)
sections("Abstract", test.abstract_count)
sections("Table Caption", test.table_intro_count)
sections("In Table Text", test.table_count)
sections("In Text Citations", test.citations_count)
sections("Bibliography", test.bibliography_count)
sections("Appendix", test.appendices_count)
sections("Keywords", test.keywords_count)
sections("Notes", test.notes_count)

report.add_paragraph("Excised words from citations\n")
for num, excised_item in enumerate(test.citation_excise_text, start = 1):

    (explanations(str(num), excised_item))
subtract_this = test.figures_count + test.abstract_count + test.table_intro_count + test.table_count+ test.citations_count+ \
    test.bibliography_count + test.appendices_count + test.keywords_count + test.notes_count

sections("Total", test.total + test.table_count)
sections("After excluding all chosen sections: ", test.total + test.table_count - subtract_this)

report.save(f'CountSci{this_file}')
#sections("Words to be excluded", )

#report.add_paragraph
#for index, items in enumerate(test.false_negatives, start= 1):
#         "{index}. {items}", file= report)
#     print("\n\nNot Counted citations", file = report)
#     for index, items in enumerate(test.citations_text, start =1):
#         print(f"{index}. {items}",file = report)
