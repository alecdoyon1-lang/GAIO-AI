import re

with open('VOID.py', 'r') as f:
    content = f.read()

# 1. Find and extract the function from the end
function_start = content.find('# ─── Context-Aware Chatbot Response Generator ──')
function_end_marker = '    return response'
# Find the last occurrence of this marker
function_end = content.rfind(function_end_marker) + len(function_end_marker)

if function_start == -1 or function_end == -1:
    print("Function not found")
    exit(1)

function_text = content[function_start:function_end]

# 2. Update the function signature to include visibility_data
old_signature = 'def generate_chatbot_response(user_input, scores, seo_data, lso_data, gaio_data, smo_data, \n                               discovered_keywords, recommendations):'
new_signature = 'def generate_chatbot_response(user_input, scores, seo_data, lso_data, gaio_data, smo_data, \n                               discovered_keywords, recommendations, visibility_data):'
function_text = function_text.replace(old_signature, new_signature)

# 3. Add grade letter calculations after visibility_score extraction
old_weakest = '    # Identify weakest areas\n    scores_dict = {"SEO": seo_score, "LSO": lso_score, "GAIO": gaio_score, "SMO": smo_score}\n    weakest = min(scores_dict, key=scores_dict.get)'
new_weakest = '    # Calculate grade letters\n    on_page_letter = score_to_grade(scores["on_page_grade"])[0]\n    visibility_letter = score_to_grade(visibility_score)[0]\n    \n    # Identify weakest areas\n    scores_dict = {"SEO": seo_score, "LSO": lso_score, "GAIO": gaio_score, "SMO": smo_score}\n    weakest = min(scores_dict, key=scores_dict.get)'
function_text = function_text.replace(old_weakest, new_weakest)

# 4. Remove the old function from the end
# Find the newline after the function
newline_after = content.find('\n', function_end) + 1
content = content[:function_start] + content[newline_after:]

# 5. Insert the updated function before Render Dashboard
render_dashboard_marker = '# ─── Render Dashboard ─────────────────────────────────────────────────────────'
content = content.replace(render_dashboard_marker, function_text + '\n\n' + render_dashboard_marker)

# 6. Update the function call to pass visibility_data
old_call = 'response = generate_chatbot_response(user_input, scores, seo_data, lso_data, gaio_data, smo_data, \n                                          discovered_keywords, recommendations)'
new_call = 'response = generate_chatbot_response(user_input, scores, seo_data, lso_data, gaio_data, smo_data, \n                                          discovered_keywords, recommendations, visibility_data)'
content = content.replace(old_call, new_call)

with open('VOID.py', 'w') as f:
    f.write(content)

print("File updated successfully")