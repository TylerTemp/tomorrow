$(document).ready(function(evt)
{
  var info_panel = $("#info-panel");
  var email_input = $("#email-input");
  var resend_btn = $("#resend-btn");
  var email_btn = $("#email-btn");
  var name_btn = $("#name-btn");
  var pwd_btn = $("#pwd-btn");

  var set_error = function(msg, error)
  {
    if (!msg)
      return info_panel.parent().hide();
    var cls = error? "danger": "success";
    info_panel.html(
      '<div class="am-alert am-alert-' + cls + '" data-am-alert>' +
        '<button type="button" class="am-close">&times;</button>' +
        '<p>' + msg + '</p>' +
      '</div>'
    );
    info_panel.parent().show();
  }

  var ajax = function(data, btn)
  {
    $.ajax(
      settings = {
        'data': data,
        'type': 'post',
        'beforeSend': function(jqXHR, settings)
        {
          jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
          btn.prop("disabled", true).button("loading");
          set_error();
        }
      }
    ).done(function(data, textStatus, jqXHR)
    {
      var obj = $.parseJSON(data);
      if (obj.error == 0)
        set_error(_('A verify email has been sent to "{0}"').format(obj.email), false);
      else if (obj.error == 1)
        set_error(_('You need to verify your email first'), true);
      else if (obj.error == 2)
        set_error(_('Oops, we failed to send email to "{0}", sorry for that').format(obj.email), true);
      else if (obj.error == 3)
        set_error(_('Nothing to resend'), false);
      else
        set_error(_('Oops, unexpected error ({0}), sorry for that').format(obj.error), true);
    }).fail(function(jqXHR, textStatus, errorThrown)
    {
      set_error(
        _("Sorry, a server error occured, please refresh and retry") +
        " (" +
        jqXHR.status +
        ": " +
        errorThrown +
        ")",
        true
      );
    }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
    {
      btn.prop("disabled", false).button('reset');
    });
  }

  name_btn.click(function(evt)
  {
    evt.preventDefault();
    var data = {'action': 'name'};
    ajax(data, $(this));
  });

  pwd_btn.click(function(evt)
  {
    evt.preventDefault();
    var data = {'action': 'pwd'};
    ajax(data, $(this));
  });

  email_btn.click(function(evt)
  {
    evt.preventDefault();
    var data = {'action': 'email', 'email': email_input.val()};
    ajax(data, $(this));
  });

  resend_btn.click(function(evt)
  {
    evt.preventDefault();
    var data = {'action': 'resend'};
    ajax(data, $(this));
  });

});
