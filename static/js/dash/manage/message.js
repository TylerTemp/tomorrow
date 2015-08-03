$(function()
{
  var set_error = function($field, msg, level)
  {
    if (level)
      level = 'am-alert-' + level;
    var $alert = $field.find(".am-comment-bd .am-alert");
    if (!$alert.length)
    {
      if (!msg)
        return;
      var $alert = $('<div class="am-alert" data-am-alert><button type="button" class="am-close">&times;</button><p></p></div>')
        .appendTo($field.find('.am-comment-bd')).hide();
    }
    $alert.removeClass('am-alert-success am-alert-warning am-alert-danger am-alert-secondary')
          .addClass(level || '');
    if (msg)
      return $alert.fadeIn(200).find('p').html(msg);
    return $alert.hide();
  }

  var make_comment = function(obj, sent)
  {
    var result = '<li class="am-comment ' + (sent? 'am-comment-flip': '') + '">';
    var display_user = sent? 'to': 'from';
    var other_user = sent? 'from': 'to';
    if (!obj[display_user])
      result += '<span class="am-comment-avatar am-btn am-btn-primary am-icon-user-plus"></span>';
    else if (obj[display_user].indexOf('@') != -1)
      result += '<a class="am-comment-avatar am-btn am-btn-warning" href="mailto:' + obj[display_user] + '"><span class="am-icon-envelope-o"></span></a>';
    else
      result += '<a href="/hi/' + obj[display_user] + '/message/">'+
                  '<img class="am-comment-avatar" src="' + (obj[display_user + '_avatar'] || '/static/img/user.jpg') + '"/>' +
                '</a>';
    result += '<div class="am-comment-main">' +
                '<header class="am-comment-hd">' +
                  '<div class="am-comment-meta">';

    if (!obj[display_user])
      result += '<div class="am-comment-author am-inline"><span class="am-icon-star"> System</span></div>';
    else
      result += '<u><a class="am-comment-author" href="/hi/' + obj[display_user] + '/message/" class="am-comment-author">' + obj[display_user] + '</a></u>';

    result += (
      ' | <time datetime=" ' + obj['time_attr'] + '">' + obj['time_read'] + '</time>' +
      '</div></header>' +
      '<div class="am-comment-bd">' +
        '<form class="am-form am-g-collapse" method="post">' +
          '<fieldset>' +
            '<input type="hidden" name="action" value="modify">' +
            '<input type="hidden" name="_xsrf" value="' + obj['_xsrf'] + '">' +
            '<input type="hidden" name="id" value="' + obj['_id'] + '">' +
            '<div class="am-g-collapse">' +
              '<div class="am-form-group am-u-sm-12 am-u-md-6 am-form-icon">' +
                '<i class="am-icon-download"></i>' +
                '<input class="am-form-field" name="send-to" placeholder="Administor" value="' + (obj['to'] || obj['to_email'] || '') + '">' +
              '</div>' +
              '<div class="am-form-group am-u-sm-12 am-u-md-6 am-form-icon">' +
                '<i class="am-icon-upload"></i>' +
                '<input class="am-form-field" name="send-by" placeholder="Administor" value="' + (obj['from'] || obj['from_email'] || '') + '">' +
              '</div>' +
            '</div>' +

            '<div class="am-g-collapse">' +
              '<div class="am-from-group am-input-group am-u-sm-12 am-u-md-6 am-form-icon">' +
                '<i class="am-icon-calendar"></i>' +
                '<input type="text" placeholder="mm/dd/yy(' + _('Default: today') + '" name="date" value="' +  obj['date_read'] + '" data-am-datepicker="{ ' + (locale == 'zh'? '': "locale: 'en_US', ") + ' autoClose: 0, format: \'mm/dd/yy\'}" style="padding-left:25px;"/>' +
              '</div>' +
              '<div class="am-from-group am-u-sm-12 am-u-md-6 am-form-icon">' +
                '<i class="am-icon-clock-o"></i>' +
                '<input type="text" placeholder="HH:MM:SS(' + _('Default: now') + ')" name="time" value="' + obj['time_pick'] + '" style="padding-left:25px;">' +
              '</div>' +
            '</div>' +

            '<div class="am-g-collapse">' +
              '<div class="am-form-group am-u-sm-12">' +
                '<textarea name="content" class="am-margin-top" style="height:100px" required placeholder="' +  _('Enter the message content') + ' (&#xe603; ' +  _('MarkDown Syntax Supported')  + ')">' +
                  obj['content'] +
                '</textarea>' +
              '</div>' +
            '</div>' +

            '<div class="am-form-group am-u-sm-12">' +
              '<label class="am-checkbox">' +
                '<input type="checkbox" name="sender-deleted"  ' + (obj['sender_delete']? 'checked': '') + '>' + _('Sender Deleted') +
              '</label>' +
            '</div>' +
            '<div class="am-form-group am-u-sm-12">' +
              '<label class="am-radio-inline">' +
                '<input type="radio" name="receiver-status" value="-1" ' + (obj['receiver_status'] == -1? 'checked': '') + '>' +  _('Read') +
              '</label>' +
              '<label class="am-radio-inline">' +
                '<input type="radio" name="receiver-status" value="0" ' + (obj['receiver_status'] == 0? 'checked': '') + '>' +  _('Unread') +
              '</label>' +
              '<label class="am-radio-inline">' +
                '<input type="radio" name="receiver-status" value="1" ' + (obj['receiver_status'] == 1? 'checked': '') + '>' +  _('Deleted') +
              '</label>' +
            '</div>' +
            '<div class="am-form-group am-cf">' +
              '<button type="submit" class="am-btn am-btn-primary am-fr" data-am-loading="{spinner:\'refresh\', loadingText: \'\'}">' +
                '<span class="am-icon-save"></span>' +
              '</button>' +
              '<button class="am-btn am-btn-warning am-fr am-margin-right" data-role="delete" data-am-loading="{spinner:\'cog\', loadingText: \'\'}">' +
                '<span class="am-icon-trash"></span>' +
              '</button>' +
            '</div>' +
          '</fieldset>' +
        '</form>' +
      '</div>' +
    '</div>' +
  '</li>');

    return result;
  }

  var on_click_delete_btn = function(evt)
  {
    evt.preventDefault();
    var $self = $(this);
    var $fieldset = $self.closest('fieldset');
    var id = $fieldset.find('input[name="id"]').val();
    $self.button('loading');
    $fieldset.prop('disabled', true);
    console.log($self.data('id'));
    $.ajax(setting={
      data: {
        action: 'delete',
        id: id,
        _xsrf: $fieldset.find('input[name="_xsrf"]').val()
      },
      method: 'post',
      'beforeSend': function(jqXHR, settings)
      {
        jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
      }
    }).done(function(data, textStatus, jqXHR)
    {
      console.log(data);
      var $comment = $self.closest('li.am-comment');
      $comment.fadeOut(300, $comment.remove);
    }).fail(function(jqXHR, textStatus, errorThrown)
    {
      var msg = _("Sorry, a server error occured, please refresh and retry") +
                  " ({0}: {1})".format(jqXHR.status, errorThrown);
      try
      {
        var obj = $.parseJSON(jqXHR.responseText);
      }
      catch (e)
      {
        return append_error($fieldset, msg, 'danger');
      }
      if (obj.error & 2)
      {
        msg = _('Message not exist');
      }
      return append_error($fieldset, msg, 'danger');
    }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
    {
      $self.button('reset');
      $fieldset.prop('disabled', false);
    });
  }

  var on_modify_submit = function(evt)
  {
    evt.preventDefault();
    var $form = $(this);
    console.log($form);
    var $li_comment = $form.closest('li.am-comment');
    var $fieldset = $form.find('fieldset');
    var $submit_btn = $form.find('button[type="submit"]');
    var is_sent = $li_comment.hasClass('am-comment-flip');
    var values = {};
    $.each($form.serializeArray(), function(i, field)
    {
      values[field.name] = field.value;
    });
    console.log(values);

    $fieldset.prop('disabled', true);
    $submit_btn.button('loading');
    $.ajax(setting={
      data: values,
      method: 'post',
      'beforeSend': function(jqXHR, settings)
      {
        jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
      }
    }).done(function(data, textStatus, jqXHR)
    {
      var obj = $.parseJSON(data);;
      var html = make_comment(obj, is_sent);
      $li_comment.fadeOut(300, function()
      {
        var $new = $(html);
        $li_comment.replaceWith($new).fadeIn(300);
        $new.find('[data-role="delete"]').click(on_click_delete_btn);
        $new.find('form').submit(on_modify_submit);
        $new.find('[data-am-datepicker]').datepicker();
      });
      // $li_comment.replaceWith('<pre>' + html + '</pre>');
      return ;
    }).fail(function(jqXHR, textStatus, errorThrown)
    {
      var msg = _("Sorry, a server error occured, please refresh and retry") +
                  " ({0}: {1})".format(jqXHR.status, errorThrown);
      try
      {
        var obj = $.parseJSON(jqXHR.responseText);
      }
      catch (e)
      {
        return append_error($fieldset, msg, 'danger');
      }
      var errors = [];
      var error = obj.error;
      if (error & 32)
        errors.push(_('Message not exist'));
      if (error & 16)
        errors.push(_('Sender not exist'));
      if (error & 1)
        errors.push(_('Receiver not exists'));
      if (error & 64)
        errors.push(_('Invalid time format'));
      if (error & 128)
        errors.push(_('Invalid date format'));
      return append_error($fieldset, 'ERROR: ' + errors.join('; '), 'danger');
    }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
    {
      $submit_btn.button('reset');
      $fieldset.prop('disabled', false);
    });
  }

  $.each($('li.am-comment form'), function(idx, ele)
  {
    var $form = $(ele);
    $form.find('[data-role="delete"]').click(on_click_delete_btn);
    $form.submit(on_modify_submit);
  });

  var $select_container = $('div.am-selected.am-dropdown');
  $('.admin-content').css(
    'min-height',
    $select_container.find('.am-selected-content.am-dropdown-content').height()
                           + $select_container.position().top
                           + 30);
  var $send_tab = $('#send-tab');
  $send_tab.css(
    'min-height',
    $send_tab.find('.am-selected-content.am-dropdown-content').eq(0).height()
    + $send_tab.find('.am-selected.am-dropdown').eq(0).position().top
    + 100
  );



  var $select_user_info = $('#select-user');
  var cache = {};
  $select_user_info.change(function(evt)
  {
    var name = $select_user_info.val() || null;
    var $sent_comment = $('#sent-tab .am-comments-list');
    var $received_comment = $('#received-tab .am-comments-list');
    var loading_html = '<div class="am-text-xxxl" style="text-align:center"><i class="am-icon-spinner am-icon-pulse"></i> {0}</div>'.format(_('loading...'));

    var fill_in = function()
    {
      var received = cache[name]['received'];
      var sent = cache[name]['sent'];

      $received_comment.html('');
      $sent_comment.html('');
      $.each(received, function(idx, elem)
      {
        $(make_comment(elem, true)).appendTo($received_comment);
      });
      $.each(sent, function(idx, elem)
      {
        $(make_comment(elem)).appendTo($sent_comment);
      });
    }

    var check_or_bind = function()
    {
      var alert = '<div class="am-alert" data-am-alert>' +
                    '<button type="button" class="am-close">&times;</button>' +
                      '{0}' +
                  '</div>';

      if (!$received_comment.find('li').length)
        $received_comment.html(alert.format(_("You have no unread message")));
      else
      {
        $.each($received_comment.find('form'), function(idx, ele)
        {
          $form = $(ele);
          $form.find('[data-role="delete"]').click(on_click_delete_btn);
          $form.submit(on_modify_submit);
          $form.find('[data-am-datepicker]').datepicker();
        });
      }
      if (!$sent_comment.find('li').length)
        $sent_comment.html(alert.format(_("You havn't sent any message or all messages have been deleted")));
      else
      {
        $.each($sent_comment.find('form'), function(idx, ele)
        {
          $form = $(ele);
          $form.find('[data-role="delete"]').click(on_click_delete_btn);
          $form.submit(on_modify_submit);
          $form.find('[data-am-datepicker]').datepicker();
        });
      }
    }

    $sent_comment.html(loading_html);
    $received_comment.html(loading_html);
    if (!cache[name])
    {
      console.log('load ' + name + ' from server');
      $.ajax(setting={
        data: {
          name: name
        },
        method: 'get'
      }).done(function(data, textStatus, jqXHR)
      {
        // console.log(data);
        var obj = $.parseJSON(data);
        cache[obj.name] = {'received': obj.receive, 'sent': obj.sent};
        fill_in();
        check_or_bind();
      }).fail(function(jqXHR, textStatus, errorThrown)
      {
        var msg = _("Sorry, a server error occured, please refresh and retry") +
                 " ({0}: {1})".format(jqXHR.status, errorThrown);
        var str = '<div class="am-alert am-alert-danger" data-am-alert>' + msg + '</div>';
        $sent_comment.html(str);
        $received_comment.html(str);
        return;
      });
    }
    else
    {
      console.log('load ' + name + ' from cache');
      fill_in();
      check_or_bind();
    }
  });

  var append_error = function($field, msg, level)
  {
    if (level)
      level = 'am-alert-' + level;
    $('<div class="am-alert ' + (level || '') + '" data-am-alert>' +
        '<button type="button" class="am-close">&times;</button>' +
        '<p>' + msg + '</p>' +
      '</div>').appendTo($field);
  }

  $('#send-tab form').submit(function(evt)
  {
    evt.preventDefault();
    var $self = $(this);
    var validated = $self.data('amui.validator').isFormValid();
    if (validated.state !== undefined)
      validated = (validated.state() == 'resolved');
    if (!validated)
      return false;
    var values = {};
    var $fieldset = $self.find('filedset');
    var $submit_btn = $self.find('button[type="submit"]');

    $.each($self.serializeArray(), function(i, field)
    {
        var name = field.name;
        if (['send-to', 'method'].indexOf(name) != -1)
        {
          if (values[name] === undefined)
            values[name] = [];
          values[name].push(field.value);
        }
        else
          values[name] = field.value;
    });

    $fieldset.prop('disabled', true);
    $submit_btn.button('loading');

    $.ajax(setting={
      data: values,
      method: 'post'
    }).done(function(data, textStatus, jqXHR)
    {
      console.log(data);
      var obj = $.parseJSON(data);
      if (obj['<error>'] && 16)
      {
        return append_error($self, _("Sender not found"), 'danger')
      }

      var use_msg = obj['msg'];
      var use_email = obj['email'];
      delete obj['<error>'];
      delete obj['msg'];
      delete obj['email'];

      for (var each in obj)
      {

        var sub_obj = obj[each];
        var err = sub_obj.error;
        if (err == 0)
          append_error($self, _('Send to {0}/{1} successfully').format(sub_obj.name, sub_obj.email), 'success');
        else
        {
          var send_msg_failed = use_msg && ((err & 1) || (err & 2));
          var send_email_failed = use_email && (err & 4) || (err & 8);
          var msgs = [];
          if (err & 1)
            msgs.push(_('User does not exist'));
          if (err & 2)
            msgs.push(_('User does not have a name and cannot receive message').format(sub_obj.name));
          if (err & 4)
            msgs.push(_('User does not have an email account'));
          if (err & 8)
            msgs.push(_('Failed to send email to {0}').format(sub_obj.email));

          var notification = undefined;
          var level = undefined;
          if (send_msg_failed && send_email_failed)
          {
            notification = _('Failed to send message({0}) and email({1})').format(sub_obj.name, sub_obj.email);
            level = 'danger';
          }
          else if (send_msg_failed && (!send_email_failed))
          {
            notification = _('Sending email({0}) secceed but sending message({1}) failed').format(
              sub_obj.email, sub_obj.name
            );
            level = 'warning';
          }
          else if ((!send_msg_failed) && send_email_failed)
          {
            notification = _('Sending message({0}) secceed but sending email({1}) failed').format(
              sub_obj.name, sub_obj.email
            );
            level = 'warning';
          }
          else
          {
            console.error(sub_obj);
          }

          append_error($self, notification + ': ' + msgs.join('; '), level);
        }
      }
    }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
    {
      $fieldset.prop('disabled', false);
      $submit_btn.button('reset');
    }).fail(function(jqXHR, textStatus, errorThrown)
    {
      var msg = _("Sorry, a server error occured, please refresh and retry") +
               " ({0}: {1})".format(jqXHR.status, errorThrown);
      append_error($self, msg, 'danger');
    });
  });
});
