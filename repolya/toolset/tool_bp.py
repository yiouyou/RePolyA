from langchain.tools import tool
from langchain.tools import StructuredTool

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.callbacks import get_openai_callback

from repolya.toolset.tool_latent import ACTIVE_LATENT_TEMPLATE, ACTIVE_LATENT_TEMPLATE_ZH

from unittest.mock import patch
from openai.error import RateLimitError


_bp_10 = {
    "Company Purpose": "Define your company in a single declarative sentence.",
    "Problem": "Describe the pain of your customer (or the customer's customer). Outline how the customer addresses the issue today and what are the shortcomings of current solutions.",
    "Solution": "Why is your value prop unique and compelling? Why will it endure? Provide use cases.",
    "Why Now": "Set up the historical evolution of your category. Why hasn't your solution been built before now? Define recent trends that make your solution possible.",
    "Market Potential": "Identify your customer and your market. Calculate the TAM (top-down), SAM (bottoms-up), and SOM.",
    "Competition/Alternatives": "Who are your direct and indirect competitors? List competitive advantages. Show that you have a plan to win.",
    "Product": "Product line-up (form factors, functionality, features, packaging, IP). Development roadmap.",
    "Business Model": "How do you intend to thrive? Revenue model, sales&distribution model, pricing, customer list, etc.",
    "Team": "Tell the story of your founders and key team members. Board of Directors/Advisors.",
    "Financials": "If you have any, please include (P&L, Balance sheet, Cash flow, Cap table, The deal, etc.)",
    "Vision": "If all goes well, what will you have built in five years?",
}

_bp_10_zh = {
    "公司宗旨": "用一个宣告性的句子定义您的公司。",
    "市场痛点": "描述您的客户（或客户的客户）的痛点。概述客户如何处理这个问题，以及当前解决方案的不足之处。",
    "解决方案": "为什么您的价值主张是独特和引人注目的？为什么它会持久？请提供使用案例。",
    "时机": "概述公司类别的历史演变。为什么以前没有您的解决方案？最近哪些趋势使您的解决方案成为可能？",
    "市场空间": "确定您的客户和市场。计算TAM（自上而下），SAM（自下而上）和SOM。",
    "竞争态势": "谁是您的直接和间接竞争对手？列出他们的竞争优势。论述您的获胜计划。",
    "产品": "产品线（形态、功能、特点、包装、知识产权）。开发路线图。",
    "商业模式": "您打算如何繁荣发展？概述收入模型、销售和分销模型、定价、潜在客户等。",
    "团队": "讲述您的创始人和关键团队成员的故事。董事会/顾问。",
    "财务预测": "如果有的话，请附上损益表、资产负债表、现金流量表、股本结构、重要交易等。",
    "愿景": "如果一切顺利，五年后您将建立什么？",
}


# _sys = ACTIVE_LATENT_TEMPLATE_ZH.replace('<<QUERY>>', '请问可以提出哪些问题和角度？')
_sys = ACTIVE_LATENT_TEMPLATE.replace('<<QUERY>>', 'What questions and angles can you ask?')


def get_inspiration(_category, _topic):
    _human = f"""假定您正在撰写一份关于{_category}的商业BP，需要从已构建的与{_category}有关的商业案例数据库中寻找灵感，并完善自己的BP。
    
下面是在寻找"商业模式"的相关灵感时，值得思考一些问题和角度：
1. 商业模式构成：新式茶饮的核心商业模式是什么？它是如何创造价值的？这包括了哪些关键资源、关键活动和关键合作伙伴？
2. 客户群体：新式茶饮业目标的主要消费群体是哪些？他们的消费习惯、喜好和消费力如何？
3. 价值主张：新式茶饮业的独特价值主张是什么？它如何满足客户的需求并区别于竞品？
4. 销售和营销策略：新式茶饮店如何吸引和保留客户？采用了哪些有效的推广策略？
5. 收入来源：新式茶饮店的主要收入来源是什么？单一产品的定价策略如何？有无其他利润增长点（如附加值服务或产品）？
6. 成本结构：核心的成本支出是什么？如何通过效率提升或其他方式控制成本？
7. 供应链管理：新式茶饮业的供应链是怎样的？优质的原材料是如何采购的？物流和储存不同茶饮配料的方式又是如何？
8. 创新元素：新式茶饮业有哪些创新的影响力或有潜力的商业模式？这些创新如何推动企业的持续增长？
9. 竞争环境：在新式茶饮行业中，主要的竞争对手是哪些？他们的成功因素或失败因素是什么？有无可能出现新的竞争者或潜在威胁？
10. 商业可持续性：新式茶饮业对环境和社会的影响如何进行管理和减少？有无其他可持续发展的商业做法或潜在机会？

为了更全面地思考和完善新式茶饮商业BP的{_topic}部分，请问可以提出哪些问题和角度？
"""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", _sys),
            ("human", _human)
        ]
    )
    model = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
    runnable = (
        {"_category": RunnablePassthrough(), "_topic": RunnablePassthrough()} 
        | prompt 
        | model 
        | StrOutputParser()
    )
    with get_openai_callback() as cb:
        _re = runnable.invoke({"_category": _category, "_topic": _topic})
        _token_cost = f"Tokens: {cb.total_tokens} = (Prompt {cb.prompt_tokens} + Completion {cb.completion_tokens}) Cost: ${format(cb.total_cost, '.5f')}"
        return _re, _token_cost

# 在寻找灵感以完善商业模式时，可以考虑以下一些问题和角度：
# 1. 商业模式构成：新式茶饮的核心商业模式是什么？它是如何创造价值的？这包括了哪些关键资源、关键活动和关键合作伙伴？
# 2. 客户群体：新式茶饮业目标的主要消费群体是哪些？他们的消费习惯、喜好和消费力如何？
# 3. 价值主张：新式茶饮业的独特价值主张是什么？它如何满足客户的需求并区别于竞品？
# 4. 销售和营销策略：新式茶饮店如何吸引和保留客户？采用了哪些有效的推广策略？
# 5. 收入来源：新式茶饮店的主要收入来源是什么？单一产品的定价策略如何？有无其他利润增长点（如附加值服务或产品）？
# 6. 成本结构：核心的成本支出是什么？如何通过效率提升或其他方式控制成本？
# 7. 供应链管理：新式茶饮业的供应链是怎样的？优质的原材料是如何采购的？物流和储存不同茶饮配料的方式又是如何？
# 8. 创新元素：新式茶饮业有哪些创新的影响力或有潜力的商业模式？这些创新如何推动企业的持续增长？
# 9. 竞争环境：在新式茶饮行业中，主要的竞争对手是哪些？他们的成功因素或失败因素是什么？有无可能出现新的竞争者或潜在威胁？
# 10. 商业可持续性：新式茶饮业对环境和社会的影响如何进行管理和减少？有无其他可持续发展的商业做法或潜在机会？
# 这些问题和角度可以帮助您更全面地思考和完善新式茶饮商业BP的商业模式部分。通过分析和回答这些问题，您可以深入了解茶饮行业并从中获取灵感和创意。记得和商业案例数据库中的相关案例相比较和分析，以寻找最适合您的商业模式。


