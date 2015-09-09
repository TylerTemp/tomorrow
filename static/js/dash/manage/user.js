$(document).ready(function()
{
  // the default $().button will cause the button invisiable in middle
  // size screen, why?
  $.fn.btn = function(status)
  {
    var attr = eval('(' + this.data('am-loading') + ')');
    switch (status) {
      case 'loading':
        if (this.hasClass('am-loading'))
          break;
        attr.source = this.html();
        var html = '<i class="am-icon-{0} {1}"></i>{2}'.format(
          attr.spinner, (attr.pause? 'am-icon-pulse': ''), (attr.loadingText || '')
        );
        this.html(html).
          addClass('am-loading');
        this.data('am-loading', attr.toSource());
        break;
      case 'reset':
        if (!this.hasClass('am-loading'))
          break;
        var html = attr.resetText || attr.source;
        this.html(html).
          removeClass('am-loading');
        break;
    }
    return this;
  };

  $('form').each(function(index, element)
  {
    var $form = $(element);
    var id = $form.prop('id');
    var $avatar_input = $form.find('input[name="avatar"]');
    var $avatar_img = $form.parent().find('img').eq(0);
    var $change_pwd_chk = $form.find('input[name="change_pwd"]');
    var $change_pwd_input = $form.find('input[name="pwd"]');
    var $repwd_input = $form.find('input[name="repwd"]');
    var $repwd_panel = $form.find('[data-role="repwd-error"]');
    var action = $form.find('input[name="action"]').val();
    var $error_panel = $form.find('div.am-alert');

    var check_pwd = function()
    {
      var pwd = $change_pwd_input.val();
      var $group = $change_pwd_input.closest('.am-form-group');
      var $alert = $group.find('.am-icon-warning');

      if (!$alert.length)
        $alert = $('<span class="am-text-warning am-icon-warning"> </span>').hide().
          appendTo($group);
      if (!pwd)
      {
        $alert.hide();
        $group.removeClass('am-form-error').addClass('am-form-success');
        return true;
      }
      else if (pwd.length < PWD_MIN_LENGTH)
      {
        $group.removeClass('am-form-success').addClass('am-form-error');
        $alert.html(' ' + _('Password should not be less than {0} words').format(PWD_MIN_LENGTH)).show();
        return false;
      }
      $alert.hide();
      $group.removeClass('am-form-error').addClass('am-form-success');
      return true;
    }

    var set_error = function(msg, error)
    {
      if (!$error_panel.length)
      {
        if (!msg)
          return;
        $error_panel = $(
          '<div class="am-alert" data-am-alert></div>').appendTo($form);
      }
      if (!msg)
        return $error_panel.remove();

      if (error)
        $error_panel.addClass('am-alert-danger').removeClass('am-alert-success');
      else
        $error_panel.addClass('am-alert-success').removeClass('am-alert-danger');
      return $error_panel.html(msg);
    }

    var set_field_error = function($field, msg)
    {
      var $group = $field.closest('.am-form-group');
      var $alert = $group.find('.am-icon-warning');
      if (!$alert.length)
        $alert = $('<span class="am-text-warning am-icon-warning"> </span>').hide().
          appendTo($group);
      if (!msg)
      {
        $group.removeClass('am-form-error');
        return $alert.hide();
      }
      $group.removeClass('am-form-success').addClass('am-form-error');
      return $alert.html(msg).show();
    }

    var check_repwd = function()
    {
      var pwd = $change_pwd_input.val();
      var repwd = $repwd_input.val();
      // var need_chk = $change_pwd_chk.prop('checked');
      if (pwd && (repwd != pwd))
        $repwd_panel.
          show(200).
          css('display', 'block').
          html(
            ' ' + _('You need to enter the same password, you know that')
          ).
          parent().addClass('am-form-warning').removeClass('am-form-success');
      else
        $repwd_panel.hide(100).parent().removeClass('am-form-warning');

      if (pwd && (pwd == repwd))
        $repwd_panel.parent().addClass('am-form-success');

      if (pwd)
        return pwd == repwd;
      return true;
    }

    $form.validator(
    {
      onValid: function(validity)
      {
        $(validity.field).closest('.am-form-group').find('.am-icon-warning').hide();
      },
      validate: function(validity)
      {
        var $field = $(validity.field);
        validity.valid = false;
        var val = $field.val();
        switch ($field.prop('name'))
        {
          case 'user':
            if (val)
              if (val.length < USER_MIN_LEN)
                validity.customError = 'tooShort';
              else if (!RegExp($field.prop('pattern')).test(val))
                validity.patternMismatch = true;
              else
                validity.valid = true;
            else
              validity.valid = true;
            break;
          case 'email':
            if (val)
              if (!RegExp($field.prop('pattern')).test(val))
                validity.patternMismatch = true;
              else
                validity.valid = true;
            else if (action == 'invite')
              validity.valueMissing = true;
            else
              validity.valid = true;
            break;
          case 'pwd':
            var min = $field.prop('minlength') || PWD_MIN_LENGTH;
            // var max = $field.prop('maxlength');
            if (val)
              // if (val > max)
              //   validity.tooLong = true;
              if (val < min)
                validity.customError = 'tooShort';
              else
                validity.valid = true;
            else
              validity.valid = true;
            break;
        }

        // console.log($field.prop('name'));
        // console.log(validity);
        return validity;
      },

      onInValid: function(validity)
      {
        var $field = $(validity.field);
        var name = $field.prop('name');
        var $group = $field.closest('.am-form-group');
        var $alert = $group.find('.am-icon-warning');
        var msg = undefined;
        if (name == 'user')
        {
          var val = $field.val();
          // why can't I get minlength?
          var min = $field.prop('minlength') || parseInt($field.data('min-length'));
          var max = $field.prop('maxlength')

          if (validity.customError == 'tooShort')
            msg = _('User Name should not shorter than {0} characters').format(min);
          else if (validity.tooLong)
            msg = _('User Name should not longer than {0} characters').format(max);
          else if (validity.patternMismatch)
          {
            // if (val.length < min)
            //   msg = _('User Name should not shorter than {0} characters').format(min);
            // else if (val.length > max)
            //   msg = _('User Name should not longer than {0} characters').format(max);
            if (val == '..')
              msg = _("User Name should not be '..'");
            else
              msg = _('User Name should only contain English characters, Chinese characters, number, space, underbar, minus, dot');
          }
        }
        else if (name == 'email')
        {
          if (validity.valueMissing)
            msg = _('Email should not be empty');
          else if (validity.patternMismatch)
            msg = _('Hey, we only accept email address from earth');
        }

        if (!msg)
          msg = $field.data('validationMessage') || this.getValidationMessage(validity);

        if (!$alert.length)
        {
          $alert = $('<span class="am-text-warning am-icon-warning"> </span>').hide().
            appendTo($group);
        }
        $alert.html(msg).show();
      }
    });

    $form.submit(function(evt)
    {
      evt.preventDefault();
      var $self = $(this);
      var $fieldset = $self.find('fieldset');
      var validated = $self.data('amui.validator').isFormValid();
      if (validated.state !== undefined)
        validated = (validated.state() == 'resolved');
      if (validated)
      {
        var values = {};
        $.each($self.serializeArray(), function(i, field)
        {
            values[field.name] = field.value;
        });
        var action = values['action'];
        if ((action == 'invite' || $change_pwd_chk.prop('checked'))
            && !(check_repwd() && check_pwd()) )
          return false;
        if ($.isEmptyObject(values))
        {
          console.log('Unexpected sumbit');
          return false;
        }

        var $submit_btn = $self.find('button[type="submit"]');
        $submit_btn.btn('loading');
        $fieldset.prop('disabled', true);
        $.ajax(
          settings={
            data: values,
            type: 'post',
            beforeSend: function(jqXHR, settings)
            {
              jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
            }
          }
        ).done(function(data, textStatus, jqXHR)
        {
          console.log(data);
          var obj = $.parseJSON(data);
          if (obj.error == 0)
          {
            $form.find('input:checkbox[name="active"]').prop('checked', obj.active);
            $form.find('input:checkbox[name="show_email"]').prop('checked', obj.show_email);
            $form.find('input:radio[name="{0}"]'.format(obj.lang) || 'none').click();
            $form.find('input:radio[name="' + obj.group + '"]').click();
            $form.find('input:checkbox[name="ss"]').prop('checked', obj.service && ($.inArray('ss', obj.service) != -1));
            $form.find('input[name="user"]').val(obj.user || '');
            $form.find('input[name="email"]').val(obj.email || '');
            $form.find('input[name="avatar"]').val(obj.avatar || '');
            $form.find('input[name="pwd"]').val(obj.pwd);
            $form.find('input[name="repwd"]').val(obj.pwd);
            $form.find('input:checkbox[name="change_pwd"]').uCheck('uncheck');
            $form.parent().find('img').eq(0).prop('src', obj.avatar || '/static/img/user.jpg');
            if (action != 'invite')
            {
              var $panel = $form.closest('.am-panel');
              $form.find('legend').html(obj.user || '');
              $panel.find('.am-panel-title').html(obj.user || '');
            }
            return set_error(_('Update Succeed'), false);
          }
          else
          {
            if (obj.error & 2)
            {
              console.log('user exists');
              set_field_error($form.find('input[name="user"]'), _('User Name is taken. Please try another one'));
            }
            if (obj.error & 4)
            {
              console.log('email exists');
              set_field_error($form.find('input[name="email"]'), _('Email is taken. Please try another one'));
            }
          }
        }).fail(function(jqXHR, textStatus, errorThrown)
        {
          set_error(
            _("Sorry, a server error occured, please refresh and retry") +
            " ({0}: {1})".format(jqXHR.status, errorThrown),
            true
          );
        }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
        {
          $form.find('button[type="submit"]').btn('reset');
          $form.find('fieldset').prop('disabled',false);
        });
      }
      else
      {
        console.log('not submit');
        return false
      }
    });

    $repwd_input.on('input', function()
    {
      if ($form.find('input[name="action"]').val() == 'invite' || $change_pwd_chk.prop('checked'))
        return check_repwd();
    });
    $change_pwd_input.on('input', check_pwd);

    $avatar_input.blur(function(evt)
    {
      var url = $(this).val() || '/static/img/user.jpg';
      $avatar_img.prop('src', url);
    });

    $change_pwd_chk.change(function(evt)
    {
      var is_chked = $(this).prop('checked');
      $change_pwd_input.prop('disabled', (!is_chked)).focus();
      if (is_chked)
      {
        $form.find('[data-role="repwd"]').show(200);
      }
      else
      {
        $form.find('[data-role="repwd"]').hide(200);
      }
    });

    $form.find('button[data-role="delete"]').click(function(evt)
    {
      evt.preventDefault();
      var $btn = $(this);
      if ($btn.hasClass('am-loading'))
        return false;
      var id = $(this).data('id');
      var action = 'delete';
      var $fieldset = $form.find('fieldset');
      $btn.btn('loading');
      $fieldset.prop('disabled', true);
      $.ajax(settings={
        data: {
          'id': id,
          'action': 'delete'
        },
        type: 'post',
        beforeSend: function(jqXHR, settings)
        {
          jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
        }
      }).done(function(data, textStatus, jqXHR)
      {
        console.log(data);
        var obj = $.parseJSON(data);
        if (obj.error == 0)
        {
          var $panel = $form.closest('.am-panel');
          $panel.hide(200, $panel.remove);
        }
        else if (obj.error == 1)
        {
          set_error(_('User is not on the earth'), true);
        }
        else
        {
          set_error(_('Unexpected error code {0}'.format(obj.error)), true);
        }
      }).fail(function(jqXHR, textStatus, errorThrown)
      {
        set_error(
          _("Sorry, a server error occured, please refresh and retry") +
          " ({0}: {1})".format(jqXHR.status, errorThrown),
          true
        );
      }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
      {
        $btn.btn('reset');
        $fieldset.prop('disabled', false);
      });
    });
  });
});
