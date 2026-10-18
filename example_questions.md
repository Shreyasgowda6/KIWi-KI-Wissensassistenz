# KIWi — Example Questions

This file contains example questions for testing the KIWi knowledge assistant. The questions are intended to evaluate document retrieval, answer correctness, source citations, language handling, and the ability to respond when information is unavailable.

## 1. Funding Opportunities

1. What funding opportunities are available at THWS?
2. Which funding programmes are mentioned in the documents?
3. What research funding opportunities are available for THWS staff?
4. What information is available about HAW-ForschungsSchub?
5. Which documents contain information about research funding?

## 2. Deadlines and Dates

1. What is the deadline for HAW-ForschungsSchub?
2. Are there any research funding deadlines in 2027?
3. What deadlines are mentioned in the September 2026 funding newsletter?
4. What application dates are mentioned across the available documents?
5. Are different deadlines mentioned in different newsletter editions?

## 3. Application Requirements

1. What are the application requirements for HAW-ForschungsSchub?
2. What documents are required for a funding application?
3. Who is eligible to apply for the funding programmes mentioned?
4. What steps are described for applying for research funding?
5. Is there any information about the application procedure?

## 4. Questions Requiring Multiple Sources

1. What differences exist between the June and September 2026 funding newsletters?
2. Which deadlines appear in more than one document?
3. How has the funding information changed between newsletter editions?
4. Which documents provide information about the same funding programme?
5. Compare the available information about HAW-ForschungsSchub across the documents.

## 5. Source and Citation Verification

1. Which document supports the answer about the HAW-ForschungsSchub deadline?
2. On which page can I find information about research funding?
3. Which source mentions the application requirements?
4. Can you identify the documents used to answer my question?
5. What evidence in the retrieved passages supports your answer?

## 6. Questions to Test Missing Information

These questions help test whether KIWi avoids inventing answers when its indexed documents do not contain the requested information.

1. What is the deadline for the imaginary KIWi Scholarship?
2. Who won the 2026 Nobel Prize in Physics?
3. What is tomorrow's weather forecast for Würzburg?
4. What is the exact budget of a funding programme if no budget is stated in the documents?
5. What is the personal telephone number of a THWS employee if it is not listed in the documents?

**Expected behaviour:** If the retrieved context does not contain sufficient evidence, KIWi should state that the information could not be found in the documents rather than guessing. Verify this behaviour through testing.

## 7. Language Handling

1. What is the deadline for HAW-ForschungsSchub?
2. Was ist die Frist für HAW-ForschungsSchub?
3. Welche Fördermöglichkeiten werden in den Dokumenten erwähnt?
4. HAW-ForschungsSchub ಗೆ ಅರ್ಜಿ ಸಲ್ಲಿಸಲು ಕೊನೆಯ ದಿನಾಂಕ ಯಾವುದು?

KIWi should attempt to answer in the same language as the question, as specified in its system prompt.

## 8. General Retrieval Tests

1. Summarise the information about research funding.
2. Find documents related to HAW-ForschungsSchub.
3. What information is available about funding applications?
4. Which pages discuss funding deadlines?
5. What relevant information can you find about research support?

## Testing Notes

For each question, check:

- **Retrieval relevance:** Are the retrieved passages relevant to the question?
- **Answer correctness:** Is the answer supported by the original documents?
- **Citation accuracy:** Do the cited passage numbers correspond to the correct sources?
- **Page accuracy:** Do the listed page numbers identify the relevant pages?
- **Abstention:** Does KIWi avoid guessing when evidence is insufficient?
- **Language handling:** Does KIWi respond in the language of the question?

**Note:** These are proposed test questions. Their answers depend on the contents of the documents indexed by KIWi.