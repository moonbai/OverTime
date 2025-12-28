# modules/web_service/templates.py

def get_html_template(leave_types, webhook_enabled, holiday_info):
    """返回HTML模板"""
    leave_options = "".join([f'<option value="{t}">{t}</option>' for t in leave_types])

    return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>加班记录填报</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
        .container {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #1976D2; text-align: center; margin-bottom: 20px; }}
        .form-group {{ margin-bottom: 15px; }}
        label {{ display: block; margin-bottom: 5px; font-weight: bold; color: #333; }}
        input[type="text"], input[type="date"], input[type="number"], select {{ width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }}
        .radio-group {{ display: flex; gap: 15px; padding: 8px 0; }}
        .radio-group label {{ font-weight: normal; cursor: pointer; }}
        .checkbox-group {{ padding: 8px 0; }}
        .submit-btn {{ width: 100%; padding: 12px; background: #4CAF50; color: white; border: none; border-radius: 4px; font-size: 16px; cursor: pointer; margin-top: 10px; }}
        .submit-btn:hover {{ background: #45a049; }}
        .info {{ background: #e3f2fd; padding: 10px; border-radius: 4px; margin-bottom: 15px; font-size: 14px; }}
        .hidden {{ display: none; }}
        .leave-fields {{ background: #fff3e0; padding: 15px; border-radius: 4px; margin-top: 10px; }}
        .work-fields {{ background: #e8f5e9; padding: 15px; border-radius: 4px; margin-top: 10px; }}
        .note {{ color: #666; font-size: 12px; margin-top: 5px; }}
        .result {{ margin-top: 5px; font-size: 13px; color: #1976D2; font-weight: bold; min-height: 20px; }}
        .auto-detect {{ background: #E3F2FD; border: 1px solid #2196F3; padding: 8px; border-radius: 4px; margin-top: 8px; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📋 加班记录填报</h1>

        <div class="info">
            <strong>填写说明：</strong><br>
            • 选择日期后自动判断类型，可手动修改<br>
            • 事假会自动记录为休息日<br>
            • 提交后会自动跳转到成功页面<br>
            • Webhook状态: {'启用' if webhook_enabled else '禁用'}<br>
            • 节假日判断: {holiday_info}
        </div>

        <form action="/submit" method="POST">
            <div class="form-group">
                <label>用户 *:</label>
                <input type="text" name="user" required placeholder="输入您的姓名">
            </div>

            <div class="form-group">
                <label>日期 *:</label>
                <div style="display: flex; gap: 10px;">
                    <input type="date" name="date" required value="" id="date_input" style="flex: 1;" onchange="autoDetectDayType()">
                </div>
                <div id="date_result" class="result"></div>
                <div class="auto-detect">💡 选择日期后自动判断，可手动修改</div>
            </div>

            <div class="form-group">
                <label>日期类型 *:</label>
                <div class="radio-group">
                    <label><input type="radio" name="day_type" value="工作日" checked> 工作日</label>
                    <label><input type="radio" name="day_type" value="休息日"> 休息日</label>
                    <label><input type="radio" name="day_type" value="节假日"> 节假日</label>
                    <label><input type="radio" name="day_type" value="调休日"> 调休日</label>
                </div>
            </div>

            <div class="form-group">
                <div class="checkbox-group">
                    <label><input type="checkbox" name="is_leave" id="is_leave" onchange="toggleLeave()"> 是否请假</label>
                </div>
            </div>

            <div id="leave_section" class="hidden">
                <div class="leave-fields">
                    <div class="form-group">
                        <label>请假类型:</label>
                        <select name="leave_type" id="leave_type" onchange="toggleLeaveHours()">
                            <option value="">请选择</option>
                            {leave_options}
                        </select>
                    </div>

                    <div id="leave_hours_section" class="hidden">
                        <div class="form-group">
                            <label>请假时长:</label>
                            <div class="radio-group">
                                <label><input type="radio" name="leave_hours" value="-4"> 半天(-4)</label>
                                <label><input type="radio" name="leave_hours" value="-8" checked> 全天(-8)</label>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div id="work_section" class="work-fields">
                <div class="form-group">
                    <label>加班时长(小时):</label>
                    <input type="number" name="work_hours" id="work_hours" value="8" step="0.5" min="0">
                    <div class="note">非请假状态填写，休息日/节假日也可以填写</div>
                </div>
            </div>

            <button type="submit" class="submit-btn">提交记录</button>
        </form>

        <div style="margin-top: 20px; text-align: center;">
            <a href="/api/data" target="_blank">查看JSON数据</a> |
            <a href="/status" target="_blank">服务状态</a>
        </div>
    </div>

    <script>
        function toggleLeave() {{
            const isLeave = document.getElementById('is_leave').checked;
            const leaveSection = document.getElementById('leave_section');
            const workSection = document.getElementById('work_section');

            if (isLeave) {{
                leaveSection.classList.remove('hidden');
                workSection.classList.add('hidden');
            }} else {{
                leaveSection.classList.add('hidden');
                workSection.classList.remove('hidden');
            }}
        }}

        function toggleLeaveHours() {{
            const leaveType = document.getElementById('leave_type').value;
            const hoursSection = document.getElementById('leave_hours_section');

            if (leaveType === '事假') {{
                hoursSection.classList.remove('hidden');
            }} else {{
                hoursSection.classList.add('hidden');
            }}
        }}

        function autoDetectDayType() {{
            const date = document.getElementById('date_input').value;
            if (!date) return;

            const resultDiv = document.getElementById('date_result');
            resultDiv.innerHTML = "正在自动判断...";

            fetch(`/api/check_date?date=${{date}}`)
                .then(response => response.json())
                .then(data => {{
                    if (data.error) {{
                        resultDiv.innerHTML = "❌ " + data.error;
                        resultDiv.style.color = "#F44336";
                    }} else {{
                        resultDiv.innerHTML = `✓ 自动检测: ${{data.type}} (${{data.reason}})`;
                        resultDiv.style.color = "#4CAF50";

                        const radioButtons = document.querySelectorAll('input[name="day_type"]');
                        radioButtons.forEach(radio => {{
                            if (radio.value === data.type) {{
                                radio.checked = true;
                            }}
                        }});
                    }}
                }})
                .catch(error => {{
                    resultDiv.innerHTML = "❌ 判断失败: " + error;
                    resultDiv.style.color = "#F44336";
                }});
        }}

        window.addEventListener('load', function() {{
            setTimeout(function() {{
                const today = new Date().toISOString().split('T')[0];
                document.getElementById('date_input').value = today;
                autoDetectDayType();
            }}, 500);
        }});
    </script>
</body>
</html>
"""
