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

var set_user_error = function(error, is_email)
{
  var user_obj = $("#user-or-email");
  switch(error)
  {
    case 'empty':
      set_error(user_obj, _("User Name or Email should not be empty"), "error");
      break;
    case 'notexist':
      if (is_email)
        set_error(user_obj, _("This email hasn't <a href='/signin/'>registered</a>"), "error");
      else
        set_error(user_obj, _("This user name hasn't <a href='/signin/'>registered</a>"), "error");
      break;
    default:
      set_error(user_obj);
  };
}

var set_pwd_error = function(error)
{
  var pwd_obj = $("#pwd");
  switch(error)
  {
    case 'empty':
      set_error(pwd_obj, _("Password should not be empty"), "error");
      break;
    case 'wrong':
      set_error(pwd_obj, _("Password incorrect"), "error");
      break;
    default:
      set_error(pwd_obj);
  }
}


var enterSubmit = function(evt)
{
  if (evt.keyCode == 13)
    $('form').submit();
}


$(document).ready(function(){
  var user   = $("#user-or-email");
  var pwd  = $("#pwd");
  var remember = $("#remember-me");
  var submit = $("#submit");
  var server_error_panel = $("#server-error");

  user.on('input', function(evt)
  {
    if (!$(this).val())
      return set_user_error('empty');
    set_user_error();
  });
  pwd.on('input', function(evt)
  {
    if (!$(this).val())
      return set_pwd_error('empty');
    set_pwd_error();
  });

  user.keyup(enterSubmit);
  pwd.keyup(enterSubmit);
  submit.click(function(evt){  $('form').submit();  });

  $('form').submit(function(evt)
  {
    var u = user.val(), p = pwd.val();
    if (!(u && p))
      return false;
    $.ajax(
      settings = {
        'data': {
          'user': user.val(),
          'pwd': pwd.val(),
          'remember': remember.prop("checked")
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

      if (obj.error & MASK_USER_EMPTY)
        set_user_error('empty', false);
      else if (obj.error & MASK_USER_NOT_EXISTS)
        set_user_error("notexist", false);
      else if (obj.error & MASK_EMAIL_NOT_EXISTS)
        set_user_error("notexist", true);
      else if (obj.error & MASK_EMAIL_NOT_EXISTS)
        set_user_error("exists", true);

      if (obj.error & MASK_PWD_EMPTY)
        set_pwd_error("empty");
      else if (obj.error & MASK_PWD_WRONG)
        set_pwd_error("wrong");

    }).fail(function(jqXHR, textStatus, errorThrown)
    {
      server_error_panel.text(
        _("Sorry, a server error occured, please refresh and retry") +
        " (" +
        jqXHR.status +
        ": " +
        errorThrown +
        ")"
      );
      server_error_panel.show(400);
    }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
    {
      submit.button('reset');
    });
    return false;
  });
});
