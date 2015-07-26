$(document).ready(function(evt)
{
  $("form").validator(
  {
    onValid: function(validity)
    {
      $(validity.field).closest('.am-form-group').find('.am-icon-warning').hide();
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
        // why I can't get minlength?
        var min = $field.prop('minlength') || PWD_MIN_LENGTH;
        var max = $field.prop('maxlength');
        if (validity.valueMissing)
          msg = _('User Name should not shorter than {0} characters').format(min);
        if (validity.patternMismatch)
        {
          if (val.length < min)
            msg = _('User Name should not shorter than {0} characters').format(min);
          else if (val.length > max)
            msg = _('User Name should not longer than {0} characters').format(max);
          else if (val == '..')
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
      else if (name == 'pwd')
      {
        if (validity.valueMissing)
        {
          var min = $field.prop('minlength') || PWD_MIN_LENGTH;
          msg = _('Password should not be less than {0} words').format(min);
        }
      }
      if (!msg)
        msg = $field.data('validationMessage') || this.getValidationMessage(validity);

      if (!$alert.length)
      {
        $alert = $('<span class="am-text-warning am-u-sm-10 am-icon-warning"> </span>').hide().
          appendTo($group);
      }

      $alert.html(msg).show();
    }
  });

  var set_specific_error = function(name, msg)
  {
    var $field = $('form').find('input[name="{0}"]'.format(name));
    var $group = $field.closest('.am-form-group');
    var $alert = $group.find('.am-icon-warning');
    if (!$alert.length)
    {
      $alert = $('<span class="am-text-danger am-u-sm-10 am-icon-warning"> </span>').hide().
        appendTo($group);
    }
    if (!msg)
    {
      $group.removeClass('am-form-error');
      return $alert.hide();
    }
    $group.removeClass('am-form-success').addClass('am-form-error');
    $alert.html(msg).show(200);
  }

  var set_general_error = function(msg)
  {
    var $error_panel = $("#error-panel");
    if (!msg)
      return $error_panel.hide(200);
    $error_panel.html(msg).show(200);
  }

  $('form').submit(function(evt)
  {
    evt.preventDefault();
    var $self = $(this);
    var $fieldset = $self.find('fieldset');
    if ($self.data('amui.validator').isFormValid())
    {
      var $submit_btn = $("#submit");
      var values = {};
      $.each($self.serializeArray(), function(i, field)
      {
          values[field.name] = field.value;
      });

      $submit_btn.button("loading");
      set_general_error();
      $fieldset.prop('disabled', true);
      $.ajax(
        settings = {
          'data': values,
          'type': 'post',
          'beforeSend': function(jqXHR, settings)
          {
            jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
          }
        }
      ).done(function(data, textStatus, jqXHR)
      {
        console.log(data);
        var obj = $.parseJSON(data);
        if (obj.error == 0)
          return (window.location.href = (obj.redirect || '/'));
        if (obj.error & 1)
          set_general_error(
            _("Oops, your verify code just expired. Be quicker next time")
          );
        if (obj.error & 2)
          set_specific_error(
            'user',
            _('User Name is taken. Please try another one')
          );
        if (obj.error & 4)
          set_specific_error(
            'email',
            _('Email exists. Please <a href="/login/">login</a> directly or <a href="/lost/">find your password</a>')
          );
      }).fail(function(jqXHR, textStatus, errorThrown)
      {
        console.log(errorThrown);
        var info = _("Sorry, a server error occured, please refresh and retry") +
          " ({0}: {1})".format(jqXHR.status, errorThrown);
        set_general_error(info);
      }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
      {
        $fieldset.prop('disabled', false);
        $submit_btn.button("reset");
      });

    }
  });

});
