$(document).ready(function()
{
  var set_info = function(container, msg, level)
  {
    if(!msg)
      return container.html('');
    var cls = level? 'am-alert-'+level: '';
    return container.html(
      '<div class="am-alert ' + cls + '" data-am-alert>' +
        '<button type="button" class="am-close">&times;</button>' +
        '<p>' + msg + '</p>' +
      '</div>'
    );
  }
  $("button[data-role='delete']").click(function(evt)
  {
    evt.preventDefault();
    var btn = $(this);
    var id = btn.data('id');
    var container = btn.closest('.container');
    var collapse = $("#" + id);
    var info_panel = collapse.find('[data-role="info-panel"]');
    var _set_info = function(msg, level)
    {
      set_info(info_panel, msg, level);
    }

    $.ajax(
      settings = {
        'data': {
          'id': id,
          'action': 'delete'
        },
        'type': 'post',
        'beforeSend': function(jqXHR, settings)
        {
          btn.button('loading');
          jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
        }
      }
    ).done(function(data, textStatus, jqXHR)
    {
      var obj = $.parseJSON(data);
      if (obj.error == 0)
        return container.hide(400, function(evt)
        {
          container.remove();
        });
      collapse.collapse('open');
      return _set_info(
        _("Sorry, Unknown error") + ':({0})'.format(obj.error),
        'danger');
    }).fail(function(jqXHR, textStatus, errorThrown)
    {
      console.log('open');
      collapse.collapse('open');
      return _set_info(
        _("Sorry, a server error occured, please refresh and retry") +
          " ({0}: {1})".format(jqXHR.status, errorThrown),
        'danger');
    }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
    {
      btn.button('reset');
    });
  });

  $("button[data-role='edit']").click(function(evt)
  {
    evt.preventDefault();
    var btn = $(this);
    var id = btn.data('id');
    var container = btn.closest('.container');
    var undo_btn = container.find('button[data-role="undo"]');
    var collapse = $("#" + id);
    var info_panel = collapse.find('div[data-role="info-panel"]');
    var tbody = collapse.find('tbody');
    var for_edit = (btn.data('status') == 'edit')

    if (for_edit)
    {
      btn.data('status', 'save').html('<span class="am-icon-save"></span>');
      collapse.collapse('open');
      undo_btn.show(400).attr('disabled', false);
    }
    else
    {
      btn.data('status', 'edit').html('<span class="am-icon-pencil"></span>');
      undo_btn.hide(400).attr('disabled', true);
    }

    var title = tbody.find('td[data-role="title"]');
    var show_email = tbody.find('td[data-role="show-email"]');
    var reprint = tbody.find('td[data-role="reprint"]');
    if (for_edit)
    {
      var t = title.find('a').hide().text();
      title.find('input').show().val(t);

      var show_email_val = (show_email.data('true') !== undefined);
      show_email.children(':first-child').hide();
      show_email.children(':nth-child(2)').show().find('input').uCheck(show_email_val? 'check': 'uncheck');
    }
  });


  $("button[data-role='undo']").click(function(evt)
  {
    evt.preventDefault();
    var btn = $(this);
    var container = btn.closest('.container');
    var save_btn = container.find('button[data-role="edit"]');
    var tbody = container.find('tbody');

    btn.prop('disabled', true).hide();
    save_btn.removeClass('am-active').data('status', 'edit').html('<span class="am-icon-pencil"></span>');
    var title = tbody.find('td[data-role="title"]');
    title.find('a').show();
    title.find('input').hide();

    var show_email = tbody.find('td[data-role="show-email"]');
    show_email.children(':first-child').show();
    show_email.children(':nth-child(2)').hide();

    var reprint = tbody.find('td[data-role="reprint"]');
    reprint.children(':first-child').show();
    reprint.children(':nth-child(2)').hide();
  });
});
