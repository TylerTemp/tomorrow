var set_error = function(obj, msg, level)
{
  var container = obj.parent();
  var panel = container.children(".error-panel");

  container.removeClass("am-form-success");
  container.removeClass("am-form-warning");
  container.removeClass("am-form-error");
  if (level)
    container.addClass("am-form-"+level);

  if (msg)
  {
    panel.show(400);
    panel.html(msg);
  }
  else
    panel.hide(400);
}

var set_user_error = function(error)
{
  var user_obj = $("#user");
  switch(error){
    case 'empty':
      set_error(user_obj, _("User Name should not be empty"), "error");
      break;
    case 'dot':
      set_error(user_obj, _("User Name should not be '.' or '..'"), "error");
      break;
    case 'length':
      set_error(user_obj, _("User Name should not longer than {0} characters").format(USER_MAX_LEN), "error");
      break;
    case 'format':
      set_error(user_obj, _("User Name should only contain English characters, Chinese characters, number, space, underbar, minus, dot, and can not only be '.' or '..'"), "error");
      break;
    case 'exists':
      set_error(user_obj, _("User Name is taken. Please try another one"), "error");
      break;
    default:
      set_error(user_obj);
  }
}

var check_user = function()
{
  var user_obj = $("#user");
  var val = user_obj.val();
  if (!val)
  {
    set_user_error('empty');
    return false;
  }
  if (val == '.' || val == '..')
  {
    set_user_error('dot');
    return false;
  }
  if (val.length > USER_MAX_LEN)
  {
    set_user_error('length');
    return false;
  }
  if (!USER_RE.test(val))
  {
    set_user_error('format');
    return false;
  }
  set_user_error();
  return true;
}


var set_email_error = function(error)
{
  var email_obj = $("#email");
  switch(error)
  {
    case 'empty':
      set_error(email_obj, _("Email should not be empty"), "error");
      break;
    case 'format':
      set_error(email_obj, _("Wrong email format"), "error");
      break;
    case 'exists':
      set_error(email_obj, _('Email exists. Please <a href="/login/">login</a> directly or <a href="/lost/">find your password</a>'), "error");
      break;
    default:
      set_error(email_obj);
  }
}


var check_email = function()
{
  var email_obj = $("#email");
  var val = email_obj.val();
  if (!val)
  {
    set_email_error("empty");
    return false;
  }
  else if(!EMAIL_RE.test(val))
  {
    set_email_error("format");
    return false;
  }
  set_email_error();
  return true;
}


var set_pwd_error = function(error)
{
  var pwd_obj = $("#pwd");
  switch(error)
  {
    case 'empty':
      set_error(pwd_obj, _("Password should not be empty"), "error");
      break;
    default:
      set_error(pwd_obj);
  }
}

var check_pwd = function()
{
  var pwd_obj = $("#pwd");
  if (!pwd_obj.val())
  {
    set_pwd_error("empty");
    return false;
  }
  set_pwd_error(pwd_obj);
  return true;
}

var check_repwd = function()
{
  var repwd = $("#re-pwd");
  var pwd   = $("#pwd");
  var reval = repwd.val();
  var pwdval=  pwd.val();
  if ((reval == '') && (pwdval == ''))
  {
    set_error(repwd);
    return false;
  }
  if (reval != pwdval)
  {
    set_error(repwd, _("Re-entered password is not the same"), "warning");
    return false;
  }
  set_error(repwd, null, "success");
  return true;
}

var enterSubmit = function(evt)
{
  if (evt.keyCode == 13)
    $('form').submit();
}


$(document).ready(function(){
  var user   = $("#user");
  var email  = $("#email");
  var pwd    = $("#pwd");
  var repwd  = $("#re-pwd");
  var submit = $("#submit");
  var server_error_panel = $("#server-error");

  user.blur(check_user);
  email.blur(check_email);
  pwd.blur(check_pwd);

  user.keyup(enterSubmit);
  email.keyup(enterSubmit);
  pwd.keyup(enterSubmit);
  repwd.keyup(enterSubmit);

  repwd.on('input', check_repwd);
  pwd.on('input', function()
  {
    if (repwd.val())
      check_repwd();
  });
  submit.click(function(evt){  $('form').submit();  });
  $('form').submit(function(evt)
  {
    var u = check_user(), e = check_email(), p = check_pwd(), r = check_repwd();
    if (!(u && e && p && r))
      return false;
    $.ajax(
      settings = {
        'data': {
          'user': user.val(),
          'email': email.val(),
          'pwd': pwd.val()
        },
        'type': 'post',
        'beforeSend': function(jqXHR, settings){
          jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
          submit.button("loading");
          server_error_panel.hide(400);
        }
      }
    ).done(function(data, textStatus, jqXHR)
    {
      var obj = $.parseJSON(data);
      server_error_panel.hide(400);
      if (obj.error == 0)
        return window.location.href = obj.redirect;

      if (obj.error & MAST_SEND_EMAIL_FAILED)
      {
        server_error_panel.html(
          _('Looks like the register is done but we failed to send an activating email. We are trying to fix that. You can visit') +
          ' <u><a href="' + obj.redirect + '">' + _('here') + '</a></u> ' +
          _('to retry')
        );
        server_error_panel.show(400);
      }
      else if (obj.error & MASK_USER_EMPTY)
        set_user_error('empty');
      else if (obj.error & MASK_USER_TOO_LONG)
        set_user_error("length");
      else if (obj.error & MASK_USER_FORMAT_WRONG)
        set_user_error("format");
      else if (obj.error & MASK_USER_EXISTS)
        set_user_error("exists");


      if (obj.error & MASK_EMAIL_EMPTY)
        set_email_error("empty");
      else if (obj.error & MASK_EMAIL_FORMAT_WRONG)
        set_email_error("format");
      else if (obj.error & MASK_EMAIL_EXISTS)
        set_email_error("exists");

      if (obj.error & MASK_PWD_EMPTY)
        set_pwd_error("empty");

    }).fail(function(jqXHR, textStatus, errorThrown)
    {
      server_error_panel.text(
        _("Sorry, a server error occured, please refresh and retry") +
        " ({0}: {1})".format(jqXHR.status, errorThrown)
      );
      server_error_panel.show(400);
    }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
    {
      submit.button('reset');
    });
    return false;
  });
});
