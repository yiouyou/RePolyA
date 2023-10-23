import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.append(_RePolyA)

from repolya._const import AUTOGEN_REF
from repolya.autogen.workflow import create_rag_task_list, search_faiss_openai
from repolya.autogen.util import cost_usage
from repolya.rag.qa_chain import qa_with_context, summerize_text
from autogen import ChatCompletion

import time

start_time = time.time()

ChatCompletion.start_logging(reset_counter=True, compact=False)

_query = "who, when and why fired Frank from Cloudeon?"

_task_list = create_rag_task_list(_query)
print(f"\n\ntask_list:\n{_task_list}")

_context = search_faiss_openai(_task_list)
print(f"\n\ncontext:\n{_context}")

_qa, _tc = qa_with_context(_query, _context)
print(f"\n\nqa_with_context:\n{_qa}\n\n{_tc}")

_sum, _tc = summerize_text(_context, 'stuff')
print(f"\n\nsummerize_text:\n{_sum}\n\n{_tc}")

end_time = time.time()
execution_time = end_time - start_time
_time = f"Time: {execution_time:.1f} seconds"
print(_time)

# _2 = """
# A: Who fired Frank from Cloudeon?
# Q: According to the provided context, it is stated that Frank Mogensen terminated his own employment with UAB Cloudeon. It is mentioned that he confirmed the effects of termination and reconfirmed his termination in emails. There is no mention of him being fired by anyone else.

# A: When was Frank fired from Cloudeon?
# Q: Frank Mogensen was terminated from his position at UAB Cloudeon on April 5, 2022, as per his letter dated April 5, 2022.

# A: Why was Frank fired from Cloudeon?
# Q: According to the provided context, it is stated that Frank Mogensen's employment with Cloudeon was terminated due to his counter-productive attitude towards the CEO and unacceptable behavior towards employees in Lithuania. It is also mentioned that Frank Mogensen artificially invented a dispute around his employment as part of a plan to quit the group without taking the initiative, while still obtaining maximum earn-out payment. Additionally, there were tensions and disagreements between Frank Mogensen and the management team, leading to a decision to remove him from his position.

# A: What was Frank's role or position at Cloudeon?
# Q: Frank Mogensen held multiple roles and positions at Cloudeon. He was initially the CEO of Cloudeon and later took on the position of CTO. He was also a co-founder and majority shareholder in the company.

# A: Were there any previous incidents or warnings leading up to Frank's termination?
# Q: Yes, there were previous incidents and warnings leading up to Frank's termination. It is mentioned in the provided context that Frank Mogensen had and deliberately utilized an unacceptable temper, which caused approximately 15 employees to resign. It was also stated that employee satisfaction was very low, and it was difficult to hire new employees because they did not want to work in a company where Frank Mogensen was present. Additionally, there were emails and correspondence indicating that Frank Mogensen's behavior was a problem and that he had received letters of resignation from employees who threatened to leave if his behavior was not addressed."""
# _31, _tc = qa_with_context(_query, _2)
# print(f"\n\nqa_with_context:\n{_31}\n\n{_tc}")
# _32, _tc = summerize_text(_2, 'stuff')
# print(f"\n\nsummerize_text:\n{_32}\n\n{_tc}")

print(f"cost_usage: {cost_usage(ChatCompletion.logged_history)}")

