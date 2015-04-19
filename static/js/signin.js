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
        panel.text(msg);
    }
    else
        panel.hide(400);
}

var check_user = function()
{
    var user_obj = $("#user");
    if (!user_obj.val())
    {
        set_error(user_obj, _("User Name should not be empty"), "error");
        return false;
    }
    set_error(user_obj, null, null);
    return true;
}

var check_email = function()
{
    var email_obj = $("#email");
    var val = email_obj.val();
    if (!val)
    {
        set_error(email_obj, _("Email should not be empty"), "error");
        return false;
    }
    else if(!EMAIL_RE.test(val))
    {
        set_error(email_obj, _("Wrong email format"), "error");
        return false;
    }
    set_error(email_obj, null, null);
    return true;
}

var check_pwd = function()
{
    var pwd_obj = $("#password");
    if (!pwd_obj.val())
    {
        set_error(pwd_obj, _("Password should not be empty"), "error");
        return false;
    }
    set_error(pwd_obj, null, null);
    return true;
}

var check_repwd = function()
{
    var repwd = $("#re-password");
    var pwd   = $("#password");
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

$(document).ready(function(){
    var user   = $("#user");
    var email  = $("#email");
    var pwd    = $("#password");
    var repwd  = $("#re-password");
    var submit = $("#submit");
    user.blur(check_user);
    email.blur(check_email);
    pwd.blur(check_pwd);
    user.keyup(function(evt)
    {
        if (evt.keyCode == 13)
            $('form').submit();
    });
    email.keyup(function(evt)
    {
        if (evt.keyCode == 13)
            $('form').submit();
    });
    pwd.keyup(function(evt)
    {
        if (evt.keyCode == 13)
            $('form').submit();
    });
    repwd.keyup(function(evt)
    {
        if (evt.keyCode == 13)
            $('form').submit();
    });
    repwd.on('input', check_repwd);
    pwd.on('input', function()
    {
        if (repwd.val())
            check_repwd();
    });
    submit.click(function(evt){$('form').submit();});
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
                    'pwd': pwd.val(),
                    '_xsrf': $.cookie('_xsrf'),
                    'ajax': true,
                },
                'type': 'post',
                'beforeSend': function(jqXHR, settings){
                    jqXHR.setRequestHeader('X-Xsrftoken', $.cookie('_xsrf'));
                    submit.prop("disabled", true);
                    submit.button(_("loading"));
                }
            }
        ).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
        {
            console.log(data_jqXHR);
            console.log(textStatus);
            console.log(jqXHR_errorThrown);
            submit.prop("disabled", false);
            submit.button('reset');
        });
        return false;
    });
});
