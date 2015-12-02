var shuffle = function(array)
{
  // BY: Fisher-Yates
  // https://github.com/coolaj86/knuth-shuffle
  var currentIndex = array.length;
  var temporaryValue;
  var randomIndex;

  // While there remain elements to shuffle...
  while (0 !== currentIndex)
  {
    // Pick a remaining element...
    randomIndex = Math.floor(Math.random() * currentIndex);
    currentIndex -= 1;

    // And swap it with the current element.
    temporaryValue = array[currentIndex];
    array[currentIndex] = array[randomIndex];
    array[randomIndex] = temporaryValue;
  }

  return array;
};

var descend_str = function(a, b)
{
  var a_length = a.length;
  var b_length = b.length;
  //if (a_length == b_length)
  //  return a < b;

  var min_index = a_length > b_length? b_length - 1: a_length - 1;
  var sub_a = a.substring(0, min_index);
  var sub_b = b.substring(0, min_index);
  if (sub_a == sub_b)
    return a_length < b_length;
  return a < b;
};

$(function ()
{
// <Controller>
  var Controller = function()
  {

  };
// </Controller>

// <TagSelector>
  // <init>
  var TagSelector = function($table_body, $bar){
    this.tags = {};
    this.shown_id = [];
    this.id_to_word = {};
    this.$table_body = $table_body;
    this.$bar = $bar;
  };

  TagSelector.prototype.tags;
  TagSelector.prototype.shown_id;
  TagSelector.prototype.id_to_word;
  TagSelector.prototype.$table_body;
  TagSelector.prototype.$bar;
  // </init>

  // <load tag>
  TagSelector.prototype.load = function(tag, ok_callback, fail_callback, always_callback)
  {
    var self = this;
    // <cache>
    if (this.tags[tag] !== undefined)
    {
      if (ok_callback)
        ok_callback(this.tags[tag]);
      if (always_callback)
        always_callback();
    }
    // </cache>
    // <ajax>
    console.log('from server: ' + tag);
    var ajax = $.ajax(settings={
      data: {'tag': tag},
      type: 'get'
    }).done(function(data, textStatus, jqXHR)
    {
      var result = $.parseJSON(data);
      self.tags[tag] = result;
      self.add_words(result);
      self.render_words(result, 20);
      if (ok_callback)
        ok_callback(result);
    });
    if (fail_callback)
      ajax.fail(fail_callback);
    if (always_callback)
      ajax.always(always_callback);
    // </ajax>
  };
  // <load tag>

  // <add words to obj>
  TagSelector.prototype.add_words = function(words)
  {
    for (var index in words)
    {
      var word_obj = words[index];
      this.id_to_word[word_obj.id] = word_obj;
    }
  };
  // </add words to obj>

  // <render words>
  TagSelector.prototype.render_words = function(words, offset)
  {
    // <get string>
    var shown = this.shown_id;
    var total = words.length;
    offset = offset || 0;
    var rest = 100 -  offset;
    var html_collect = [];
    for (var index in words)
    {
      var rate = (index + 1) * rest / total + offset;
      this.render_bar(rate);
      var word_obj = words[index];
      var id = word_obj.id;
      if (shown.indexOf(id) !== -1)
        continue;
      html_collect.push(this.get_render_string(word_obj));
      this.shown_id.push(word_obj.id);
    }
    // </get string>
    // <insert>
    var $html = $(html_collect.join(''));
    $html.find('input[type="checkbox"]').uCheck('check');
    this.$table_body.prepend($html);
    // </insert>
  };
  // <render words>

  // <get word string>
  TagSelector.prototype.get_render_string = function(word)
  {
    // <parse meaning>
    var meanings = [];
    for (var type in word.meaning)
    {
      var mean = word.meaning[type].join('; ');
      meanings.push((type? '&lt;' + type + '&gt; ': '') + mean);
    }
    // </parse meaning>

    // <parse tags>
    var tags = [];
    for (var index in word.tag)
    {
      var $badge = '<span class="am-badge">' + word.tag[index] + '</span>';
      tags.push($badge);
    }
    // </parse tags>

    // <string>
    return (
      '<tr>'+
        '<td>' +
          '<label class="am-checkbox">' +
            '<input type="checkbox" data-am-ucheck data-id="' + word.id + '">' +
          '</label>' +
        '</td>' +
        '<td>' + word.spell.join(' / ') + '</td>' +
        '<td>' + meanings.join('<br/>') + '</td>' +
        '<td>' + (word.pronounce? ('[' + word.pronounce + ']'): '<span class="am-icon-times"></span>') + '</td>' +
        '<td>' + tags.join(' ') + '</td>' +
      '</tr>'
    );
    // </string>
  };
  // </get word string>

  // <process bar>
  TagSelector.prototype.render_bar = function(num, content, error)
  {
    var $bar = this.$bar;
    var text;
    if (content)
      text = content;
    else
      text = '' + num + '%';

    if (num)
      $bar.css('width', '' + num + '%');

    $bar.html(text);

    if (error)
      $bar.addClass('am-progress-bar-danger');
    else
      $bar.removeClass('am-progress-bar-danger');
  };
  // </process bar>

  // <callback result>
  TagSelector.prototype.report = function(callback)
  {
    var $checked_inputs = this.$table_body.find('input[type="checkbox"]:checked');
    var words = [];
    var id_2_word = this.id_to_word;
    $checked_inputs.each(function()
    {
      var this_id = $(this).data('id');
      var this_word = id_2_word[this_id];
      if (this_word === undefined)
      {
        alert('ERROR: Empty id ' + this_id);
      }
      words.push(this_word);
    });
    callback(words);
  };
  // </callback result>
// </TagSelector>

// <Config>
  // <init>
  var Config = function($form)
  {
    this.$form = $form;
    this.spell_word = null;
    this.choose_word = null;
    this.choose_meaning = null;
    this.order = null;
    this.repeat_till_right = null;
    this.click_to_go = null;
    this.show_chars = null;
    this._get_result();
  };

  Config.prototype.$form;
  Config.prototype.spell_word;
  Config.prototype.choose_word;
  Config.prototype.choose_meaning;
  Config.prototype.order;
  Config.prototype.repeat_till_right;
  Config.prototype.click_to_go;
  Config.prototype.show_chars;
  // </init>

  // <refresh status>
  Config.prototype._get_result = function()
  {
    var $form = this.$form;
    this.spell_word = $form.find('input[name="spell"]').prop('checked');
    this.choose_word = $form.find('input[name="choose-word"]').prop('checked');
    this.choose_meaning = $form.find('input[name="choose-meaning"]').prop('checked');
    this.order = $form.find('input[name="order"]:checked').val();
    this.repeat_till_right = $form.find('input[name="repeat-till-right"]').prop('checked');
    this.click_to_go = $form.find('input[name="click-to-go"]').prop('checked');
    var show_chars = $form.find('input[name="show-chars"]').val();
    if (show_chars)
      this.show_chars = parseInt(show_chars);
    else
      this.show_chars = 0;
  };
  // </refresh status>

  // <callback result>
  Config.prototype.report = function(callback)
  {
    this._get_result();
    return callback(this);
  };
  // </callback result>

// </Config>

// <Question>
  // <init>
  var Question = function($input_form, $choose_form)
  {
    this.$input_form = $input_form;
    this.$choose_form = $choose_form;
  };

  Question.prototype.$input_form;
  Question.prototype.$choose_form;
  // </init>

  // <set input>
  Question.prototype.set_input = function(display)
  {
    this.reset();
    var $input_form = this.$input_form;
    $input_form.show();
    this.$choose_form.hide();
    $input_form.find('#question-meaning-spell').html(display);
  };
  // </set input>

  // <set choose>
  Question.prototype.set_choose = function(display, options)
  {
    this.reset();
    var $choose_form = this.$choose_form;
    $choose_form.show();
    this.$input_form.hide();
    $choose_form.find('#question-choose').html(display);
    $choose_form.find('input[type="radio"]').each(function(index)
    {
      var value = options[index];
      if (value === undefined)
      {
        $(this).parent().hide();
        return;
      }

      var prefix = null;
      switch (index)
      {
        case 0:
          prefix = 'A';
          break;
        case 1:
          prefix = 'B';
          break;
        case 2:
          prefix = 'C';
          break;
        case 3:
          prefix = 'D';
          break;
      }

      $(this).html(prefix + '. ' + value);
    });
  };
  // </set choose>

  // <reset>
  Question.prototype.reset = function()
  {
    this.$input_form.find('input[type="text"]').val("");
    this.$choose_form.find('radio').prop('checked', false).parent().show();
    this.$input_form.find('[type="submit"]')
        .removeClass('am-icon-times am-btn-danger')
        .addClass('am-icon-check am-btn-primary');
    this.$choose_form.find('[type="submit"]')
        .removeClass('am-icon-times am-btn-danger')
        .addClass('am-icon-check am-btn-primary');
  };

  Question.prototype.not_right = function()
  {
    this.$input_form.find('[type="submit"]')
        .addClass('am-icon-times am-btn-danger')
        .removeClass('am-icon-check am-btn-primary');
    this.$choose_form.find('[type="submit"]')
        .addClass('am-icon-times am-btn-danger')
        .removeClass('am-icon-check am-btn-primary');
  };
  // </reset>
// </Question>

// <Display>
  // <init>
  var Display = function()
  {
    var $display = $('#display');
    this.$bar = $display.find('#display-bar');
    this.$text = $display.find('#display-text');
  };

  Display.prototype.$bar;
  Display.prototype.$text;
  // </init>

  // <reset>
  Display.prototype.reset = function()
  {
    this.$bar.html('')
             .removeClass('am-progress-bar-danger')
             .css('width', '0');
    this.$text.html('');
  };
  // </reset>

  // <process bar>
  Display.prototype.render_bar = function(num, content, error)
  {
    var $bar = this.$bar;
    content = content || '';

    if (num)
      $bar.css('width', '' + num + '%');

    $bar.html(content);

    if (error)
      $bar.addClass('am-progress-bar-danger');
    else
      $bar.removeClass('am-progress-bar-danger');
  };
  // </process bar>

  // <text>
  Display.prototype.set = function(shown, num, label, error)
  {
    shown = shown || '';
    this.$text.html(shown);
    this.render_bar(num, label, error);
  };
  // </text>
// </Display>

// <Recorder>
  // <init>
  var Recorder = function()
  {
    var shuffle = 0;
    var ascend = 1;
    var descend = 2;
    this.words = [];
    this.current = [];
    this.next = [];  // Wrong, and need to test again
    this.record = {};  // key: word, value: array of wrong answer

    this.SHUFFLE = shuffle;
    this.ASCEND = ascend;
    this.DESCEND = descend;
    this.sort_by = shuffle;
  };
  Recorder.prototype.words;
  Recorder.prototype.current;
  Recorder.prototype.next;
  Recorder.prototype.record;
  Recorder.prototype.sort_by;
  // </init>

  // <empty>
  Recorder.prototype.empty = function()
  {
    return this.current.length && this.next.length;
  };
  // </empty>

  // <get>
    // <get spell>
  Recorder.prototype.get_spell = function()
  {
    if (! this.current.length)
      this.next_round();
    var words = this.current.pop(0);
    return words;
  };
    // </get spell>
  // </get>

  // <add next>
  Recorder.prototype.next_round = function()
  {
    this.current.concat(this.next);
    this.next = [];
    this.sort();
  };
  // </add next>

  // <sort>
  Recorder.prototype.sort = function()
  {
    var sort_by = this.sort_by;
    if (sort_by == this.SHUFFLE)
    {
      shuffle(this.current);
    }
    else if (sort_by == this.ASCEND)
    {
      this.current.sort(function(a, b) { return a.spell[0] > b.spell[0]; });
    }
    else if (sort_by == this.DESCEND)
    {
      this.current.sort(function(a, b){ return descend_str(a.spell[0], b.spell[0]); });
    }
    else if (sort_by == this.ASCEND)
    {
      this.current.sort(function(a, b){ return descend_str(b.spell[0], a.spell[0]); });
    }
  };
  // </sort>
// </Recorder>

  var $config_form = $('#config-page');
  var tag_selector = new TagSelector($('#word-list tbody'), $('#tags-loading'));
  var config = new Config($config_form);
  var question = new Question($('#form-spell'), $('#form-choose-word'));
  var display = new Display();
  var record = new Recorder();
  var $confirm_btn = $('#tag-confirm');
  $confirm_btn.click(function(event)
  {
    event.preventDefault();
    tag_selector.report(function(words) { for (var index in words) console.log(words[index])});
  });

  $config_form.submit(function(event)
  {
    event.preventDefault();
    config.report(function(config){ console.log(config); });
  });

  var $tag_select = $('#select-tags');
  $tag_select.select2({
    placeholder: _("Select Tags"),
    allowClear: true
  });
  $tag_select.on('select2:select', function(name, event)
  {
    tag_selector.render_bar(0);
    var tag = name.params.data.text;
    console.log(tag);
    $confirm_btn.button('loading');
    tag_selector.render_bar(10, _('loading'));
    tag_selector.load(
      tag,
      function(){ tag_selector.render_bar(20, _('inserting')); },
      function(jqXHR, textStatus, errorThrown)
      {
        tag_selector.render_bar(undefined, '' + jqXHR.status + ': ' + errorThrown, true);
      },
      function(){ $confirm_btn.button('reset'); tag_selector.render_bar(100); });
  });

  // <select all>
  var $select_all = $('#select-all');
  $select_all.change(function(event)
  {
    var checked = this.checked;
    $('#word-list').find('input[type="checkbox"]').prop('checked', checked);
  });
  // </select all>
});