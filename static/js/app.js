var I18N = {
    'zh_CN':
    {
        "heading level 1": "一级标题",
        "heading level 2": "二级标题",
        "heading level 3": "三级标题",
        "heading level 4": "四级标题",
        "heading level 5": "五级标题",
        "heading level 6": "六级标题",
        "added content": "新增内容",
        "deleted content": "删除内容",
        "indent content": "缩进内容",
        "unordered list item": "无序列表内容",
        "ordered list item": "有序列表内容",
        "inline code": "行内代码",
        "code block": "代码块",

        "User Name should not be empty": "用户名不能为空",
        "Email should not be empty": "邮箱不能为空",
        "Password should not be empty": "密码不能为空",
        "Re-entered password is not the same": "两次输入的密码不一致",
        "Wrong email format": "邮箱格式错误"
    }
};


var _ = function(string)
{
    var trans = I18N[locale];
    if (trans === undefined)
        return string;

    var result = trans[string];
    if (result === undefined)
        return string;

    return result;
};
