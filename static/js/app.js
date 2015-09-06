String.prototype.format = function(){
  var args = arguments;
  return this.replace(/\{(\d+)\}/g,
    function(m,i){
      return args[i];
    });
}


var I18N = {
  'zh':
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
    "User Name should not be '..'": "用户名不能为'..'",
    "User Name should not longer than {0} characters": "用户名不能多于{0}个字符",
    "User Name should not shorter than {0} characters": "用户名不能少于{0}个字符",
    "User Name or Email should not shorter than {0} characters": "用户名或邮箱不能少于{0}个字符",
    "User Name should only contain English characters, Chinese characters, number, space, underbar, minus, dot, and can not only be '.' or '..'": "用户名只能为英文/中文字符、数字、空格、下划线、减号、小数点，且不能为“.”或“..”",
    "User Name should only contain English characters, Chinese characters, number, space, underbar, minus, dot": "用户名只能为英文/中文字符、数字、空格、下划线、减号、小数点",
    "User Name is taken. Please try another one": "用户名已被占用，请尝试其它名字",
    "This user name hasn't <a href='/signin/'>signin</a>": "这个用户名尚未<a href='/signin/'>注册</a>",
    "This email hasn't <a href='/signin/'>signin</a>": "这个邮箱尚未<a href='/signin/'>注册</a>",
    "Email should not be empty": "邮箱不能为空",
    "Email is taken. Please try another one": "户名已被占用，请尝试其它邮箱",
    'Email exists. Please <a href="/login/">login</a> directly or <a href="/lost/">find your password</a>': '邮箱已注册被注册。请直接<a href="/login/">登录</a>或<a href="/lost/">找回密码</a>',
    "Wrong email format": "邮箱格式错误",
    "Password should not be less than {0} words": "密码不能少于{0}个字",
    "Re-entered password is not the same": "两次输入的密码不一致",
    "You need to enter the same password, you know that": "你得输入相同的密码，你懂的。",
    "Password incorrect": "密码错误",
    "Hey, we only accept email address from earth": "嘿，请填写来自地球的邮箱",
    "Oops, your verify code just expired. Be quicker next time": "哎哎，验证码刚刚过期了呢。下次手快点吧",

    "Refreshing page is required to change language. Refresh now?": "修改语言需要刷新页面生效。现在刷新？",

    "loading...": "载入中……",
    "loading": "载入中",
    "source": "源",
    "edit": "编辑",
    "translation": "翻译",
    "sort priority": "排序优先级",
    "(Not Set)": "(无)",
    "change translation": "修改翻译",
    "edit content": "编辑内容",
    "loading content...": "内容载入中……",
    "Sorry, unknown error": "嗯，貌似哪里出错了",
    "Sorry, a server error occured, please refresh and retry": "哎哎，服务器出错啦，也许刷新重试一下吧",
    "sort priority should be empty or number only": "排序优先级只能为数字或为空",
    "Change saved. Refresh to see the result": "修改已保存。刷新查看结果",
    "Exit full screen": "退出全屏",
    "Enter full screen": "进入全屏",
    "Same": "一致",
    "Taken":"已占用"
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


// New for AmazeUI 2.4.1
(function($) {
  'use strict';

  $(function() {
    var $fullText = $('.admin-fullText');
    $('#admin-fullscreen').on('click', function()
    {
      $.AMUI.fullscreen.toggle();
    });

    $(document).on($.AMUI.fullscreen.raw.fullscreenchange, function()
    {
      $fullText.text($.AMUI.fullscreen.isFullscreen ? _('Exit full screen') : _('Enter full screen'));
    });
  });
})(jQuery);


// read file, return $.Deferred
var readFileIntoDataurl = function(fileInfo)
{
  var thisDef = $.Deferred();
  var fReader = new FileReader();
  var type = fileInfo.type;
  var name = fileInfo.name;
  var size = fileInfo.size;

  fReader.onerror = function(e){ thisDef.reject(e, name, size, type); };
  fReader.onload = function(e){ thisDef.resolve(e.target.result, name, size, type); };
  fReader.onprogress = function(e){ thisDef.notify(e.loaded, e.total, name, size, type ); /* loader.notify(e.loaded, e.total, name, type ); */ };
  fReader.readAsDataURL(fileInfo);
  return thisDef.promise();
};


var unitSatisfy = function(size, unit, accuracy)
{
  if (unit === undefined)
    unit = 'b';
  var offset = 0;
  switch(unit.toLowerCase())
  {
    case "b": offset = 0; break;
    case "kb": offset = 1; break;
    case "mb": offset = 2; break;
    case "gb": offset = 3; break;
    case "tb": offset = 4; break;
    default: offset = 0; break;
  }
  var bit_size = (size*Math.pow(1024, offset));
  var appropriate_size;
  var appropriate_unit;
  if (bit_size<1024)
    {appropriate_size=bit_size; appropriate_unit='b';}
  else if ((bit_size>>10)<1024)
    {appropriate_size=(bit_size/1024); appropriate_unit='kb';}
  else if ((bit_size>>20)<1024)
    {appropriate_size=(bit_size/Math.pow(1024, 2)); appropriate_unit='mb';}
  else if ((bit_size>>30)<1024)
    {appropriate_size=(bit_size/Math.pow(1024, 3)); appropriate_unit='gb';}
  else if ((bit_size>>40)<1024)
    {appropriate_size=(bit_size/Math.pow(1024, 4)); appropriate_unit='tb';}
  else
    {appropriate_size=size; appropriate_unit=unit}
  if (accuracy !== undefined)
    if ((1 - Math.abs(Math.round(appropriate_size)-appropriate_size))<1)  // it's a float
      appropriate_size = appropriate_size.toFixed(accuracy);
  return [appropriate_size, appropriate_unit.toUpperCase()];
};


var logout = function(evt)
{
  var cookie = $.AMUI.utils.cookie;
  cookie.unset('user', '/');
  cookie.unset('type', '/');
  cookie.unset('email', '/');
  cookie.unset('active', '/');
  cookie.unset('service', '/');
  // cookie.unset('lang', '/');
}

var change_lang = function(lang)
{
  var cookie = $.AMUI.utils.cookie;
  cookie.unset('lang', '/');
  if (!lang)
    return ;
  cookie.set('lang', lang, undefined, '/');
}


// for login/signin
var MASK_USER_NOT_EXISTS = 64;
var USER_MAX_LEN = 100;
var USER_MIN_LEN = 2;
var MASK_USER_TOO_SHORT = 32;
var MASK_EMAIL_NOT_EXISTS = 128;
var USER_RE = /^[a-zA-Z0-9\u4e00-\u9fa5_\ \-][a-zA-Z0-9\u4e00-\u9fa5_\.\ \-]|[a-zA-Z0-9\u4e00-\u9fa5_\.\ \-][a-zA-Z0-9\u4e00-\u9fa5_\ \-]|[a-zA-Z0-9\u4e00-\u9fa5_\.\ \-]{3,100}$/;
var EMAIL_RE = /^[\w\d.+-]+@([\w\d.]+\.)+\w{2,}$/;
var MASK_USER_TOO_LONG = 2;
var MASK_USER_EXISTS = 64;
var MASK_PWD_TOO_SHORT = 256;
var MASK_USER_EMPTY = 1;
var MASK_EMAIL_EMPTY = 8;
var MASK_EMAIL_EXISTS = 128;
var MASK_EMAIL_FORMAT_WRONG = 16;
var MASK_USER_FORMAT_WRONG = 4;
var MASK_SEND_EMAIL_FAILED = 256;
var PWD_MIN_LENGTH = 8;
var MASK_PWD_WRONG = 512;

// for upload files
var MASK_NO_PERMISSION = 1;
var MASK_FILE_TOO_BIG = 2;
var MASK_FILE_DUPLICATED_NAME = 4;
var MASK_FILE_DECODE_ERROR = 8;

var IMG_ALLOW = ['jpg', 'jpeg', 'png', 'gif'];

(function($) {
  if ($.AMUI && $.AMUI.validator) {
    $.AMUI.validator.patterns = $.extend($.AMUI.validator.patterns, {
      user: USER_RE,
      email: EMAIL_RE
    });
  }
})(window.jQuery);
