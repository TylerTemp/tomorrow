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
        "User Name or Email should not be empty": "用户名或邮箱不能为空",
        "User Name should not be '.' or '..'.": "用户名不能为'.'或'..'",
        "User Name should not longer than": "用户名不能多于",
        "characters.": "个字符。",
        "User Name should only contain English characters, Chinese characters, number, space, underbar, minus, dot, and can not only be '.' or '..'.": "用户名只能为英文/中文字符、数字、空格、下划线、减号、小数点，且不能为“.”或“..”。",
        "User Name is taken. Please try another one.": "用户名已被占用，请尝试其它名字。",
        "This user name hasn't <a href='/signin/'>signin</a>.": "这个用户名尚未<a href='/signin/'>注册</a>。",
        "This email hasn't <a href='/signin/'>signin</a>.": "这个邮箱尚未<a href='/signin/'>注册</a>。",
        "Email should not be empty": "邮箱不能为空",
        'Email exists. Please <a href="/login/">login</a> directly or <a href="/lost/">find your password</a>.': '邮箱已注册被注册。请直接<a href="/login/">登录</a>或<a href="/lost/">找回密码</a>。',
        "Wrong email format": "邮箱格式错误",
        "Password should not be empty": "密码不能为空",
        "Re-entered password is not the same": "两次输入的密码不一致",
        "Password incorrect.": "密码错误。",
        "Sorry, a server error occured, please refresh and retry.": "抱歉，服务器出错，请刷新重试。"
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


var MASK_USER_NOT_EXISTS = 64;
var USER_MAX_LEN = 100;
var MASK_PWD_EMPTY = 32;
var MASK_EMAIL_NOT_EXISTS = 128;
var USER_RE = /^[a-zA-Z0-9\u4e00-\u9fa5_\.\ \-]{1,100}$/;
var EMAIL_RE = /^[\w\d.+-]+@([\w\d.]+\.)+\w{2,}$/;
var MASK_USER_TOO_LONG = 2;
var MASK_USER_EXISTS = 64;
var MASK_PWD_WRONG = 256;
var MASK_USER_EMPTY = 1;
var MASK_EMAIL_EMPTY = 8;
var MASK_EMAIL_EXISTS = 128;
var MASK_EMAIL_FORMAT_WRONG = 16;
var MASK_USER_FORMAT_WRONG = 4;
