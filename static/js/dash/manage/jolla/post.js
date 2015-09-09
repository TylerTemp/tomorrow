$(function(evt){
  $('#posts').find('[data-role="detail"]').each(function(idx, ele){
    self = $(this);
    self.on('open.collapse.amui', function(evt){
      self = $(this);
      body = self.find('.am-panel-bd');
      if (self.data('empty'))
      {
        body.html('<i class="am-icon-spinner am-icon-pulse"></i>' + _('loading...'));
        $.ajax(
          settings={
            'data': {
              'id': self.prop('id')
            },
            'type': 'get'
          }
        ).done(function(data, textStatus, jqXHR){
          var obj = $.parseJSON(data);

          var raw_html = ('<p><label>{0}</label>: [<a href="{1}">{2}</a>] <a href="{3}" target="_blank">{4} <span class="am-icon-external-link-square"></span></a></p>' +
                          '<p><label>{5}</label>: {6}</p>' +
                          '<hr class="am-divider am-divider-dashed">' +
                          '<p><label>{7}</label>: <input class="am-form-field" type="text" value="{8}"></p>'
                         ).format(
                           _('source'), obj.edit, _('edit'), obj.link, obj.title,
                           _('translation'), (obj.trans_title? '<a href="{0}">{1}</a> (<a href="{2}"><span class="am-icon-user"> {3}</span></a>)'.format(obj.trans_link, obj.trans_title, obj.trans_author_link, obj.trans_author_name): '<span class="am-icon-times"></span>'),
                           _('sort priority'), (obj.priority || '')
                         );
          body.html('');
          var prority = $(raw_html).appendTo(body).find('input');
          var option = '<select class="am-form-field" data-am-selected>{0}</select>';
          var collect = ['<option value="" {0}>{1}</option>'.format(obj.trans_title? '': 'selected', _('(Not Set)'))];
          $.each(obj.trans, function(idx, each)
            collect.push(
              '<option value="{0}" {1}>{2}</option>'.format(each.slug, each.title == obj.trans_title? 'selected': '', '[{0}] {1}'.format(each.author, each.title)))
          );

          option = $('<p><label>' + _('change translation') + '</label>: ' +
                     option.format(collect.join('')) +
                     '</p>').appendTo(body).find('select');
          $('<p><label>{0}:</label></p>'.format(_('edit content'))).appendTo(body);
          var content = $('<textarea class="am-form-field" style="height:150px;" placeholder="&#xe603; MarkDown Format Required">{0}</textarea>'.format(obj.trans_content || '')).appendTo(body);
          $('<p><label>{0}:</label></p>'.format(_('edit description'))).appendTo(body);
          var description = $('<textarea class="am-form-field" placeholder="&#xe603; MarkDown Format Required">{0}</textarea>'.format(obj.trans_description || '')).appendTo(body);
          var error_panel = $('<div></div>').appendTo(body);
          var set_error = function(msg, level)
          {
            if (!msg)
              return error_panel.html('');
            var cls = level? 'am-alert-' + level: '';
            error_panel.html(
              '<div class="am-alert ' + cls + '" data-am-alert>' +
                '<button type="button" class="am-close">&times;</button>' +
                '<p>' + msg + '</p>' +
              '</div>'
            );
          }
          var save_btn = $(
            '<p><button class="am-btn am-btn-success"><span class="am-icon-save"></span></button></p>').appendTo(body).find('button');

          option.on('change', function(evt)
          {
            slug = this.value;
            console.log('slug %s', slug);
            if (!slug)
            {
              content.prop('disabled', true);
              description.prop('disabled', true);
              description.val('');
              return content.val('');
            }
            option.prop('disabled', true);
            save_btn.prop('disabled', true);
            content.prop('disabled', true);
            description.prop('disabled', true);
            error_panel.html(
              '<i class="am-icon-spinner am-icon-pulse"></i>' + _('loading content...')
            );
            $.ajax(settings={
              data: {'slug': slug},
              type: 'get',
              beforeSend: function(jqXHR, settings)
              {
                jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
              }
            }).done(function(data, textStatus, jqXHR){
              var obj = $.parseJSON(data);
              if (obj.error == 0)
              {
                set_error();
                content.val(obj.content);
                description.val(obj.description);
                return;
              }
              else
                return set_error(_('Sorry, unknown error') + ': ' + obj.error, 'danger');
            }).fail(function(jqXHR, textStatus, errorThrown){
              return set_error(
                _("Sorry, a server error occured, please refresh and retry") +
                " ({0}: {1})".format(jqXHR.status, errorThrown),
                'danger'
              );
            }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown){
              option.prop('disabled', false);
              save_btn.prop('disabled', false);
              content.prop('disabled', false);
              description.prop('disabled', false);
            });
          });
          save_btn.click(function(evt){
            var prority_num = prority.val();
            var content_val = content.val();
            var trans_slug = option.val();
            var id = self.prop('id');
            if (prority_num && (! prority_num.match(/\d+/)))
              return set_error(_('sort priority should be empty or number only'), 'warning');
            save_btn.attr('disabled', true).html('<i class="am-icon-spinner am-icon-pulse"></i>');
            set_error();
            $.ajax(settings={
              data: {
                'prority': prority_num,
                'content': content_val,
                'description': description.val(),
                'slug': trans_slug,
                'id': id
              },
              type: 'post',
              beforeSend: function(jqXHR, settings)
              {
                jqXHR.setRequestHeader('X-Xsrftoken', $.AMUI.utils.cookie.get('_xsrf'));
              }
            }).done(function(data, textStatus, jqXHR)
            {
              var obj = $.parseJSON(data);
              if (obj.error == 0)
                return set_error(_('Change saved. Refresh to see the result'), 'success');
              else
                return set_error(_('Sorry, unknown error') + ': ' + obj.error);
            }).fail(function(jqXHR, textStatus, errorThrown){
              set_error(
                _("Sorry, a server error occured, please refresh and retry") +
                " ({0}: {1})".format(jqXHR.status, errorThrown),
                'danger'
              );
            }).always(function(data_jqXHR, textStatus, jqXHR_errorThrown){
              save_btn.attr('disabled', false).html('<span class="am-icon-save"></span>');
            });
          });
          self.data('empty', null);
        }).fail(function(jqXHR, textStatus, errorThrown)
        {
          body.html(
            '<div class="am-alert am-alert-danger" data-am-alert>' +
              '<p>' +
                _("Sorry, a server error occured, please refresh and retry") +
                " ({0}: {1})".format(jqXHR.status, errorThrown) +
              '</p>' +
            '</div>'
          );
        });
      }
    });
  });
});
