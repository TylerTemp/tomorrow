$(document).ready(function()
{
  $('[data-role="reply"]').click(function(evt)
  {
    console.log('click');
    var btn = $(this);
    var to = btn.data('name');
    $('html, body').animate({
      scrollTop: $("#user").val(to).offset().top
    }, 300);
    $("#msg").focus();
  });
  $('[data-role="delete"]').click(function(evt)
  {
    evt.preventDefault();
    var btn = $(this);
    var id = btn.data('id');
    var container = btn.closest('.am-comment');
    var panel = container.find('[data-role="info-panel"]');
    var set_info = function(msg)
    {
      if (!msg)
        return panel.html('');
      return panel.html(
        '<div class="am-alert am-alert-danger am-margin-horizontal" data-am-alert>' +
          '<button type="button" class="am-close">&times;</button>' +
          '<p>' + msg + '</p>' +
        '</div>'
      );
    }

    $.ajax(
      settings = {
        'data': {
          'action': 'delete',
          'id': id
        },
        'type': 'post',
        'beforeSend': function(jqXHR, settings)
        {
          jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
          set_info();
          btn.button('loading');
        }
      }
    ).done(function(data, textStatus, jqXHR)
    {
      console.log(data);
      var obj = $.parseJSON(data);
      if (obj.error == 0)
        return container.hide(250, function(evt)
        {
          container.remove()
        });
      return set_info(
        _('Sorry, unknown error') + ': ' + obj.error
      );
    }).fail(function(jqXHR, textStatus, errorThrown)
    {
      set_info(
        _("Sorry, a server error occured, please refresh and retry") +
        " ({0}: {1})".format(jqXHR.status, errorThrown),
        'danger'
      );
    }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
    {
      btn.button('reset');
    });


  });

  $('form').submit(function(evt)
  {
    evt.preventDefault();

    var set_info = function(msg, level)
    {
      var panel = $("#info-panel");
      if (!msg)
        return panel.html('');
      var cls = level? 'am-alert-'+level: '';
      panel.html(
        ('<div class="am-alert {0}" data-am-alert>' +
          '<button type="button" class="am-close">&times;</button>' +
          '<p>{1}</p>' +
        '</div>').format(cls, msg)
      );
    }

    var submit_btn = $("#sumbit");

    var user = $("#user").val();
    var msg = $("#msg").val();

    if (!msg)
    {
      $("#msg").parent().addClass('am-form-warning');
      set_info(_('Content should not be empty') + ' :/', 'warning');
      return false;
    }

    $("#msg").parent().removeClass('am-form-warning');

    $.ajax(
      settings = {
        'data': {
          'action': 'send',
          'user': user,
          'msg': msg
        },
        'type': 'post',
        'beforeSend': function(jqXHR, settings)
        {
          jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
          set_info();
          submit_btn.button('loading');
        }
      }
    ).done(function(data, textStatus, jqXHR)
    {
      console.log(data);
      var obj = $.parseJSON(data);
      if (obj.error == 0)
      {
        $("#user").val('');
        $("#msg").val('');
        return set_info(
          _("Send to {0} successfully").format(user? user: 'site ownder'),
          'success'
        );
      }
      else if (obj.error == 1)
        return set_info(
          _("You can't send to yourself") + ' :[',
          'warning'
        );
      else if (obj.error == 2)
        return set_info(
          _("Oops, {0} is not a registered user").format(user) + ' :(',
          'danger'
        );
      else
        return set_info(
          _("Oops, unknown error") + ' :({0})'.format(obj.error),
          'danger'
        );
    }).fail(function(jqXHR, textStatus, errorThrown)
    {
      set_info(
        _("Sorry, a server error occured, please refresh and retry") +
        " ({0}: {1})".format(jqXHR.status, errorThrown),
        'danger'
      );
    }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
    {
      submit_btn.button('reset');
    });
    return false;
  });

});
