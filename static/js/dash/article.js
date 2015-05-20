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

  var mk_reprint = function(container, name, value)
  {
    var target = $(
      '<div>' +
        '<div class="am-u-sm-3">' +
          '<input class="am-form-field" value="' + name + '" placeholder="' + _('Enter site name') + '">' +
        '</div>' +
        '<div class="am-u-sm-8">' +
          '<input class="am-form-field" value="' + value + '" placeholder="' + _('Enter URL') + '">' +
        '</div>' +
        '<div class="am-u-sm-1">' +
          '<button class="am-btn am-btn-warning delete-reprint"><span class="am-icon-times"></span></button>' +
        '</div>' +
      '</div>'
    ).appendTo(container).hide().fadeIn(400);
    target.find('button').click(function(evt){
      evt.preventDefault();
      target.fadeOut(300, function(evt)
      {
        target.remove();
      });
    });
    return target;
  }

  $('button[data-role="add-line"]').click(function(evt)
  {
    var target = $(this).closest('td[data-role="reprint"]').find('div[data-role="reprint-container"]');
    mk_reprint(target, '', '');
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

    var title = tbody.find('td[data-role="title"]');
    var show_email = tbody.find('td[data-role="show-email"]');
    var reprint = tbody.find('td[data-role="reprint"]');
    var reprint_container = reprint.find('div[data-role="reprint-container"]');
    if (for_edit)
    {
      var title_val = title.find('a').hide().text();
      title.find('input').show().val(title_val);

      var show_email_val = (show_email.data('true') !== undefined);
      show_email.children(':first-child').hide();
      show_email.children(':nth-child(2)').show().find('input').uCheck(show_email_val? 'check': 'uncheck');

      reprint.children(':first-child').hide();
      reprint.children(':nth-child(2)').show()
      reprint_container.html('');
      reprint.find('a').each(function(idx, ele)
      {
        var self = $(ele);
        mk_reprint(reprint_container, self.text(), self.prop('href'));
      });
    }
    else
    {
      var title_input = title.find('input');
      var title_val = title_input.val();
      if (!title_val)
        return set_info(
          info_panel,
          _("Title should not be empty, you know that") + ' :/',
          'warning'
        );
      title_input.hide();
      title.find('a').show().text(title_val);

      var show_email_val = show_email.children(':nth-child(2)').hide().find('input').prop('checked');
      show_email.children(':first-child').show().html(show_email_val? '&#10004;': '&#10060;');

      var reprint_urls = [];
      var reprint_obj = {};
      reprint_container.children().each(function(idx, ele)
      {
        var inputs = $(ele).find('input');
        var name = inputs.eq(0).val();
        var url = inputs.eq(1).val();
        if (name && url && reprint_obj[name] === undefined)
        {
          reprint_urls.push('<a href="{0}">{1}</a>'.format(url, name));
          reprint_obj[name] = url;
        }
      });
      reprint.children(':first-child').html(reprint_urls.join('; ')).show();
      reprint.children(':nth-child(2)').hide();

      $.ajax(
        settings = {
          'data': {
            'id': id,
            'action': 'edit',
            'title': title_val,
            'show_email': show_email_val,
            'reprint': reprint_obj
          },
          'type': 'post',
          'beforeSend': function(jqXHR, settings)
          {
            jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
            btn.button("loading");
          }
        }
      ).done(function(data, textStatus, jqXHR)
      {
        console.log(data);
      }).fail(function(jqXHR, textStatus, errorThrown)
      {
        collapse.collapse('open');
        set_info(
          info_panel,
          _("Sorry, a server error occured, please refresh and retry") +
            " ({0}: {1})".format(jqXHR.status, errorThrown),
          'danger'
        );
      }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
      {
        btn.removeClass('am-active').button('reset');
      });
    }

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
