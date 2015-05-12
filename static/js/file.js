$(document).ready(function()
{
  var file_input = $("#file");
  var file_bar = $("#bar");
  var info_panel = $("#info-panel");

  var set_info = function(msg, level)
  {
    if (!msg)
      return info_panel.html('');
    level = level? ("am-alert-"+level): '';
    return info_panel.html(
      '<div class="am-alert "' + level + ' data-am-alert>' +
        '<button type="button" class="am-close">&times;</button>' +
        '<p>' + msg + '</p>' +
      '</div>'
    );
  }
  var bar = {
    'set': function(num)
    {
      file_bar.css("width", ""+num+"%");
      return this;
    },
    'danger': function()
    {
      file_bar.removeClass('am-progress-bar-secondary')
              .removeClass('am-progress-bar-success')
              .removeClass('am-progress-bar-warning')
              .addClass('am-progress-bar-danger');
      return this;
    },
    'warning': function()
    {
      file_bar.removeClass('am-progress-bar-secondary')
              .removeClass('am-progress-bar-success')
              .addClass('am-progress-bar-warning')
              .removeClass('am-progress-bar-danger');
      return this;
    },
    'success': function()
    {
      file_bar.removeClass('am-progress-bar-secondary')
              .addClass('am-progress-bar-success')
              .removeClass('am-progress-bar-warning')
              .removeClass('am-progress-bar-danger');
      return this;
    },
    'reset': function()
    {
      file_bar.addClass('am-progress-bar-secondary')
              .removeClass('am-progress-bar-success')
              .removeClass('am-progress-bar-warning')
              .removeClass('am-progress-bar-danger');
      return this;
    }
  }

  var delfunc = function(evt)
  {
    var btn = $(this);
    var name = btn.data('name');
    $.ajax(
      settings = {
        'data': {
          'name': name,
          'action': 'delete'
        },
        'type': 'post',
        'beforeSend': function(jqXHR, settings)
        {
          jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
          btn.button('loading');
        }
      }
    ).done(function(data, textStatus, jqXHR)
    {
      console.log(data);
      var obj = $.parseJSON(data);
      if (obj.error == 0)
      {
        var rmv = btn.parents("li");
        rmv.hide(400, function(){rmv.remove()});
        return set_info(_("Delete {0} successfully").format(obj.name), 'success');
      }
      if (obj.error == 1)
        return set_info(_("Oops, can't find {0}. Sorry for that").format(obj.name), 'danger');
      if (obj.error == 2)
        return set_info(_("Oops, failed to delete {0}. Sorry for that").format(obj.name), 'danger');

    }).fail(function(jqXHR, textStatus, errorThrown)
    {
      return set_info(
        _("Sorry, a server error occured, please refresh and retry") +
        " ({0}: {1})".format(jqXHR.status, errorThrown),
        "danger"
      );
    }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
    {
      btn.button('reset');
    });
  }

  $("button.delete").click(delfunc);
  file_input.change(function(evt)
  {
    if (this.type !== 'file' || (!this.files) || (this.files.length <= 0))
      return
    bar.reset().set(5);
    var fileInfo = evt.target.files[0];
    var fileType = fileInfo.type;
    var mainType = fileType.split('/')[0];
    var subType = fileType.split('/')[1];

    // check type
    if (IMG_ONLY &&
        ((subType === undefined) ||
        (IMG_ALLOW.indexOf(subType.toLowerCase()) == -1))
       )
    {
      bar.warning();
      return set_info(
        _("{0} is not a supported image type. Only support {1}").format(fileInfo.name, IMG_ALLOW.join(", ")),
        "warning");
    }
    if (MAX_SIZE !== undefined && fileInfo.size > MAX_SIZE)
    {
      bar.warning();
      return set_info(
        _("{0} ({1}) out of supported max file size ({2})").format(
          fileInfo.name,
          unitSatisfy(fileInfo.size, 'b', 2).join(" "),
          unitSatisfy(maxSize, 'b', 2).join(" ")
        ),
        "warning"
      );
    }

    bar.set(10);
    readFileIntoDataurl(fileInfo)
    .fail(function(e, name, size, type)
    {
      bar.warning();
      set_info(_("Oops, failed to read the file"), "warning");
    })
    .progress(function(loaded, total, name, size, type)
    {
      var num = 10 + Math.round(loaded * 80 / total);
      bar.set(num);
    })
    .done(function(dataUrl, name, size, type)
    {
      bar.set(90);
      $.ajax(
        settings = {
          'data': {
            'urldata': dataUrl,
            'name': name,
            'action': 'upload'
          },
          'type': 'post',
          'beforeSend': function(jqXHR, settings)
          {
            jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
            bar.set(95);
          }
        }
      ).done(function(data, textStatus, jqXHR)
      {
        console.log(data);
        var obj = $.parseJSON(data);
        if (obj.error == 0)
        {
          bar.success();
          mknode(obj.url, obj.name, obj.size, obj.icon)
          .prependTo("#list")
          .find("button")
          .click(delfunc);

          return set_info(_("Upload {0} successfully").format(obj.name), 'success');
        }

        var errors = [];
        if (obj.error & MASK_NO_PERMISSION)
          errors.push(_("you don't have permission to upload an image"))
        if (obj.error & MASK_FILE_TOO_BIG)
          errors.push(_("file too big"))
        if (obj.error & MASK_FILE_DUPLICATED_NAME)
          errors.push(_("you already uploaded a file with the same name, server can't rename it"));
        if (obj.error & MASK_FILE_DECODE_ERROR)
          errors.push(_("server can't decode your file"));

        var errmsg = errors.join('; ') || obj.error.toString();
        set_info(_("Oops, error occured:") + " " + errmsg, "danger");

      }).fail(function(jqXHR, textStatus, errorThrown)
      {
        bar.danger();
        return set_info(
          _("Sorry, a server error occured, please refresh and retry") +
          " ({0}: {1})".format(jqXHR.status, errorThrown),
          "danger"
        );
      }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown)
      {
        bar.set(100);
      });
    })
  });
});
