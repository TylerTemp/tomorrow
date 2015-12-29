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
  //  <init>
  var Controller = function(quiz_page, config_page, finished_page)
  {
    this.quiz = quiz_page;
    this.config = config_page;
    this.finished = finished_page;
  };
  Controller.prototype.quiz;
  Controller.prototype.config;
  Controller.prototype.finished;
  // </init>
  // <change tags>
  Controller.prototype.on_change_words = function(words)
  {
    console.log('set words for quiz');
    this.quiz.set_words(words);
    this.switch_page('config');
  };
  // </change tags>

  // <change config>
  Controller.prototype.on_change_config = function(config)
  {
    var switch_as = {shuffle: this.quiz.SHUFFLE,
                     ascend: this.quiz.ASCEND,
                     descend: this.quiz.DESCEND
    };
    console.log(config);
    this.quiz.question_format = [];
    if (config.spell_word)
      this.quiz.question_format.push('spell_word');
    if (config.choose_word)
      this.quiz.question_format.push('choose_word');
    if (config.choose_meaning)
      this.quiz.question_format.push('choose_meaning');

    this.quiz.show_words = config.show_chars;
    this.quiz.repeat_wrong = config.repeat_till_right;

    this.quiz.sort_by = switch_as[config.order];
    this.quiz.put_current_back();
    this.quiz.sort();
    console.log('sorted');
    this.switch_page('quiz');
    this.quiz.next_question();
  };
  // </change config>

  Controller.prototype.switch_page = function(page)
  {
    var words = $('#words-page');
    var config = $('#config-page');
    var quiz = $('#quiz-page');
    var finished = $('#finished-page');
    words.hide();
    config.hide();
    quiz.hide();
    finished.hide();
    switch (page)
    {
      case 'quiz':
        quiz.show();
        break;
      case 'config':
        config.show();
        break;
      case 'words':
        words.show();
        break;
      case 'finished':
        finished.show();
        break;
    }
  };

  Controller.prototype.finish = function()
  {
    console.log('finished handling');
    console.log(this);
    var record = this.quiz.record;
    var words = this.quiz.words;
    console.log('words', words);
    var results = [];
    for (var id in record)
    {
      var num = record[id];
      for (var index in words)
      {
        var this_word = words[index];
        if (this_word.id == id)
        {
          var clone_word = $.extend({}, this_word);
          clone_word['error_times'] = num;
          results.push(clone_word);
          console.log('find', clone_word);
          break;
        }
      }
    }
    this.finished.set(results, words.length);
    this.switch_page('finished');
  };
// </Controller>

// <TagPage>
  // <init>
  var TagPage = function($table_body, $bar){
    this.tags = {};
    this.shown_id = [];
    this.id_to_word = {};
    this.$table_body = $table_body;
    this.$bar = $bar;
  };

  TagPage.prototype.tags;
  TagPage.prototype.shown_id;
  TagPage.prototype.id_to_word;
  TagPage.prototype.$table_body;
  TagPage.prototype.$bar;
  // </init>

  // <load tag>
  TagPage.prototype.load = function(tag, ok_callback, fail_callback, always_callback)
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

  // <add words to self.id_to_word>
  TagPage.prototype.add_words = function(words)
  {
    for (var index in words)
    {
      var word_obj = words[index];
      this.id_to_word[word_obj.id] = word_obj;
    }
  };
  // </add words to self.id_to_word>

  // <render words>
  TagPage.prototype.render_words = function(words, offset)
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
  TagPage.prototype.get_render_string = function(word)
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
  TagPage.prototype.render_bar = function(num, content, error)
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
  TagPage.prototype.report = function(callback)
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
// </TagPage>

// <ConfigPage>
  // <init>
  var ConfigPage = function($form)
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

  ConfigPage.prototype.$form;
  ConfigPage.prototype.spell_word;
  ConfigPage.prototype.choose_word;
  ConfigPage.prototype.choose_meaning;
  ConfigPage.prototype.order;
  ConfigPage.prototype.repeat_till_right;
  ConfigPage.prototype.click_to_go;
  ConfigPage.prototype.show_chars;
  // </init>

  // <refresh status>
  ConfigPage.prototype._get_result = function()
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
  ConfigPage.prototype.report = function(callback)
  {
    this._get_result();
    return callback(this);
  };
  // </callback result>

// </ConfigPage>

// <Question>
  // <init>
  var Question = function($input_form, $choose_form)
  {
    this.$input_form = $input_form;
    this.$choose_form = $choose_form;
    this.timer = null;
  };

  Question.prototype.$input_form;
  Question.prototype.$choose_form;
  Question.prototype.timer;
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
        $(this).closest('.am-radio').hide();
        return true;
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

      console.log(prefix + '. ' + value);

      var node = $(this).closest('.am-radio')[0];
      var text_node = node.childNodes[3];
      text_node.nodeValue = prefix + '. ' + value;
    });
  };
  // </set choose>

  // <reset>
  Question.prototype.reset = function()
  {
    this.$input_form.find('input[type="text"]').val("");
    this.$choose_form.find('radio').prop('checked', false).parent().show();
    this.reset_button();
    if (this.timer !== null)
    {
      clearTimeout(this.timer);
    }
  };

  Question.prototype.not_right = function()
  {
    var self = this;
    this.$input_form.find('[type="submit"]')
        .addClass('am-icon-times am-btn-danger am-animation-shake')
        .removeClass('am-icon-hand-pointer-o am-btn-primary');
    this.$choose_form.find('[type="submit"]')
        .addClass('am-icon-times am-btn-danger am-animation-shake')
        .removeClass('am-icon-hand-pointer-o am-btn-primary');
    if (this.timer !== null)
    {
      clearTimeout(this.timer);
    }
    this.timer = setTimeout(function(){ self.reset_button() }, 1500);
  };

  Question.prototype.right = function()
  {
    var self = this;
    this.$input_form.find('[type="submit"]')
        .addClass('am-icon-check am-btn-success')
        .removeClass('am-icon-hand-pointer-o am-btn-primary');
    this.$choose_form.find('[type="submit"]')
        .addClass('am-icon-check am-btn-success')
        .removeClass('am-icon-hand-pointer-o am-btn-primary');
    if (this.timer !== null)
    {
      clearTimeout(this.timer);
    }
    this.timer = setTimeout(function(){ self.reset_button() }, 1500);
  };

  Question.prototype.reset_button = function()
  {
    this.$input_form.find('[type="submit"]')
        .removeClass('am-icon-times am-btn-danger am-animation-shake am-btn-success am-icon-check')
        .addClass('am-icon-hand-pointer-o am-btn-primary');
    this.$choose_form.find('[type="submit"]')
        .removeClass('am-icon-times am-btn-danger am-animation-shake am-btn-success am-icon-check')
        .addClass('am-icon-hand-pointer-o am-btn-primary');
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

// <QuizPage>
  // <init>
  var QuizPage = function(question, display)
  {
    var shuffle = 0;
    var ascend = 1;
    var descend = 2;
    this.words = [];  // All words
    this.current = [];    // Current words pipe
    this.next = [];  // Wrong, and need to test again
    this.record = {};  // key: word, value: array of wrong answer

    this.anwser = null;    // set to list
    this.word = null;    // current testing word

    // config
    this.SHUFFLE = shuffle;
    this.ASCEND = ascend;
    this.DESCEND = descend;
    this.sort_by = shuffle;

    this.question_format = null;
    this.repeat_wrong = true;
    this.show_words = 0;

    this.question = question;
    this.display = display;

    this.finished_callback = undefined;
  };
  QuizPage.prototype.words;
  QuizPage.prototype.current;
  QuizPage.prototype.next;
  QuizPage.prototype.record;
  QuizPage.prototype.anwser;
  QuizPage.prototype.word;
  QuizPage.prototype.sort_by;
  QuizPage.prototype.question_format;
  QuizPage.prototype.repeat_wrong;
  QuizPage.prototype.show_words;
  QuizPage.prototype.qustion;
  QuizPage.prototype.display;
  QuizPage.prototype.finished_callback;
  // </init>

  // <empty>
  QuizPage.prototype.empty = function()
  {
    if (this.word)
      return false;
    return !(this.current.length || this.next.length);
  };
  // </empty>

  // <get>
    // <get word>
  QuizPage.prototype.get_word = function()
  {
    if (! this.current.length)
      this.next_round();
    var words = this.current.pop(0);
    return words;
  };
    // </get word>
  // </get>

  // <add next>
  QuizPage.prototype.next_round = function()
  {
    console.log('next round: current:', this.current.length, 'next:', this.next.length);
    this.current = this.current.concat(this.next);
    this.next = [];
    this.sort();
    console.log('next round done: current:', this.current.length);
  };
  // </add next>

  // <sort>
  QuizPage.prototype.sort = function()
  {
    var sort_by = this.sort_by;
    console.log('sort by ' + sort_by);
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

  // <set words>
  QuizPage.prototype.set_words = function(words)
  {
    this.words = words;
    this.current = words;
    this.next = [];
    this.word = null;
    this.anwser = null;
    this.sort();
    console.log('set words num', this.words.length);
  };
  // </set words>

  // <process>
  QuizPage.prototype.process = function()
  {
    var total = this.words.length ;
    return (total - this.current.length - this.next.length) / total;
  };
  // </process>

  // <next question>
  QuizPage.prototype.next_question = function()
  {
    if (this.empty())
    {
      $.event.trigger('finished');
      return false;
    }

    var word = this.get_word();
    var format = this.next_format();
    console.log('set next question', format, word);
    this.set_page(word, format);
    return true;
  };
  // </next question>

  QuizPage.prototype.next_format = function()
  {
    var result = this.question_format;
    return result[Math.floor(Math.random() * result.length)]
  };

  // <set page>
  QuizPage.prototype.set_page = function(word, format)
  {
    console.log(word);
    console.log(format);
    this.word = word;
    if (format == 'spell_word')
    {
      var displays = [];
      if (word.pronounce)
        displays.push('/ ' + word.pronounce + ' /');
      for (var type in word.meaning)
      {
        var mean = '';
        if (type)
          mean += ('&lt;' + type + '&gt;');
        mean += word.meaning[type];
        displays.push(mean);
      }
      this.question.set_input(displays.join('<br />'));
      this.anwser = word.spell;
    }
    // </spell word>
    else    // select
    {
      var to_choose = this.shuffle_4(word);
      shuffle(to_choose);
      currect = to_choose.indexOf(word);
      this.anwser = [currect];
    // <choose word>
      if (format == 'choose_word')
      {
        var displays = [];
        // if (word.pronounce)
        //   displays.push('/ ' + word.pronounce + ' /');
        for (var type in word.meaning)
        {
          var mean = '';
          if (type)
            mean += ('&lt;' + type + '&gt;');
          mean += word.meaning[type];
          displays.push(mean);
        }
        var display = displays.join('<br />');
        var to_choose_strs = [];
        console.log(to_choose);
        for (var index in to_choose)
        {
          var this_word = to_choose[index];
          console.log(this_word);
          to_choose_strs.push(
            this_word.spell.join('; ') +
            (this_word.pronounce? ' /' + this_word.pronounce + '/ ': '')
          );
        }
        this.question.set_choose(display, to_choose_strs);
        console.log(display, to_choose_strs);
      }
    // </choose word>
    // <choose meaning>
      else    // choose_meaning
      {
        var displays = [];
        var types = [];
        for (var type in word.meaning)
          if (type)
            types.push(type);
        if (types.length !== 0)
          displays.push('&lt;' + types.join('/') + '&gt;');
        displays.push(
          word.spell.join('; ') +
          (word.pronounce? ' /' + word.pronounce + '/': '')
        );

        var to_choose_str = [];
        for (var index in to_choose)
        {
          var this_word = to_choose[index];
          var meanings = [];
          for (var type in this_word.meaning)
          {
            $.merge(meanings, this_word.meaning[type]);
          }
          console.log(meanings);
          to_choose_str.push(meanings.join('; '))
        }

        this.question.set_choose(displays.join(' '), to_choose_str);
        console.log(displays, to_choose_str);
    // <choose meaning>
      }
    }
    console.log('currect anwser: ' + this.anwser);
  };
  // </set page>

  // <get random words>
  QuizPage.prototype.shuffle_4 = function(word)
  {
    if (this.current.length <= 3)
    {
      console.log('no enough on current pipe, next round');
      this.next_round();
    }

    var result = [];
    if (this.current.length <= 3)
    {
      console.log('no enough on current pipe, return all');
      console.log('current pipe', this.current);
      result = this.current.slice();
      result.push(word);
      return result;
    }

    var word_id = word.id;
    var id_2_word = {word_id: word};
    while (Object.keys(id_2_word).length < 4)
    {
      var random_item = this.current[Math.floor(Math.random() * this.current.length)];
      if (id_2_word[random_item.id] === undefined)
        id_2_word[random_item.id] = random_item;
    }

    for (var key in id_2_word)
    {
      result.push(id_2_word[key]);
    }
    return result;
  };
  // </get random words>

  // <put back>
  QuizPage.prototype.put_current_back = function()
  {
    if (this.word != null)
      this.current.unshift(this.word);
    this.word = null;
    this.anwser = null;
  };
  // </put back>

  // <check answer>
  QuizPage.prototype.check_answer = function(answer)
  {
    console.log(answer);
    console.log(this.anwser);
    //var currect = false;
    for (var index in answer)
    {
      if (this.anwser.indexOf(answer[index]) != -1)
      {
        return true;
      }
    }
    return false;
  };
  // </check answer>

  // <get answer>
  QuizPage.prototype.report_result = function(result, extra)
  {

    var correct = this.check_answer(result);
    var this_word = this.word;
    if (!correct)
    {
      var num = this.record[this.word.id] || 0;
      num += 1;
      this.record[this.word.id] = num;
      console.log(this.word.spell.join(';') + ' -> ' + num);
      if (this.repeat_wrong)
      {
        console.log('wrong, put back', this.word);
        this.next.push(this.word);
      }
    }

    this.word = null;

    var has_question = this.next_question();
    if (!has_question)
      return ;

    if (!correct)
    {
      console.log('not right');
      this.question.not_right();
    }
    else
      this.question.right();
    this.set_process(this.process(), correct, this_word, extra);
    console.log('next word');
  };
  // </get answer>

  QuizPage.prototype.finished = function()
  {
    this.finished_callback(this.record);
  };

  // <set process>
  QuizPage.prototype.set_process = function(process, correct, word, extra)
  {
    var display = this.display;
    var ratio = (process * 100).toFixed();
    if (ratio > 100)
      ratio = 100;
    //shown, num, label, error
    var shown = null;
    if (!correct)
    {
      var spell = word.spell.join('; ');
      var pronounce = word.pronounce? (' /' + word.pronounce + '/ '): '';
      var means = [];
      for (var key in word.meaning)
      {
        if (key)
          means.push('&lt;' + key + '&gt; ');
        means.push(word.meaning[key].join(';'));
      }
      var mean = means.join('<br />');
      shown = ('Oops, your anwser (<span class="am-text-danger">' + extra + '</span>) is wrong: <br />'  +
               spell + pronounce + '<br />' +
               mean);
    }
    display.set(shown, ratio, ratio + '%', !correct);
  };
  // </set process>

// </QuizPage>

// <FinishedPage>
  var FinishedPage = function()
  {
    this.page = $('#finished-page-content');
  };
  FinishedPage.prototype.page;

  FinishedPage.prototype.set = function(record, words_num)
  {
    var cls = ['', 'am-progress-bar-secondary', 'am-progress-bar-success', 'am-progress-bar-warning',
               'am-progress-bar-danger'];
    var cls_num = cls.length;
    var total = 0;
    for (var index in record)
    {
      var this_word = record[index];
      total += this_word.error_times;
    }

    var sub_bars = [];
    var t_rows = [];
    for (var index in record)
    {
      var word = record[index];
      var num = word.error_times;
      console.log(word, num);
      var this_cls = cls[index % cls_num];
      var ratio = (num * 100 / total).toFixed();
      var spell = word.spell.join(';');

      sub_bars.push(
        '<div class="am-progress-bar ' + this_cls + '" style="width: ' + ratio + '%">' +
          spell + ' ' + num +
        '</div>'
      );

      var meanings = [];
      for (var type in word.meaning)
      {
        var t = type? '&lt;' + type + '&gt; ': '';
        meanings.push(t + word.meaning[type].join(';'));
      }

      t_rows.push(
        '<tr>' +
          '<td>' + spell + '</td>' +
          '<td>' + (word.pronounce || '' ) + '</td>' +
          '<td>' + word.error_times + '</td>' +
          '<td>' + meanings.join('<br />') + '</td>' +
        '</tr>'
      );
    }
    //var sum = '<p><b>Total:</b>' + total + '/' + words_num + '</p>';
    var right_num = words_num - record.length;
    var total_ratio = (right_num * 100 / words_num).toFixed();
    var shown_in_end = total_ratio < 50;
    var label = 'Accuracy: ' + right_num + '/' + words_num + '(' + total_ratio + '%)';
    var sum = (
      '<div class="am-progress">' + (shown_in_end? label: '') +
        '<div class="am-progress-bar am-progress-bar-success" style="width: ' + total_ratio + '%">' + (shown_in_end? '': label) + '</div>' +
      '</div>');
    var bar = '<div class="am-progress">' + sub_bars.join('') + '</div>';
    var table = (
      '<table class="am-table am-table-bordered am-table-striped am-table-hover am-table-compact">' +
        '<thead><tr>' +
          '<th>' + _('Word') + '</th>' +
          '<th>' + _('Pronounce') + '</th>' +
          '<th>' + _('Wrong Times') + '</th>' +
          '<th>' + _('Meaning') + '</th>' +
        '</tr></thead>' +
        '<tbody>' +
          t_rows.join('') +
        '</tbody>' +
      '</table>'
    );
    this.page.html(sum + bar + table);
  };
// </FinishedPage>

  var $spell_form = $('#form-spell');
  var $choose_form = $('#form-choose-word');

  var tag_page = new TagPage($('#word-list tbody'), $('#tags-loading'));

  var $config_form = $('#config-page');
  var config_page = new ConfigPage($config_form);

  var question = new Question($spell_form, $choose_form);

  var display = new Display();

  var quiz_page = new QuizPage(question, display);

  var finished_page = new FinishedPage();

  var controller = new Controller(quiz_page, config_page, finished_page);
  $(document).on('finished', function(){ controller.finish.call(controller) });

  var $confirm_btn = $('#tag-confirm');
  $confirm_btn.click(function(event)
  {
    event.preventDefault();
    tag_page.report(function(words){ controller.on_change_words(words); });
  });

  $config_form.submit(function(event)
  {
    event.preventDefault();
    config_page.report(function(config){ controller.on_change_config(config); });
  });

  $spell_form.submit(function(event)
  {
    event.preventDefault();
    $form = $(this);
    var result = $form.find('[name="answer"]').val();
    quiz_page.report_result(result.split(';'), result);
  });

  $choose_form.submit(function(event)
  {
    event.preventDefault();
    $form = $(this);
    var $result = $form.find('[name="answer"]:checked');
    var result = $result.val();
    var extra = $result.closest('label').text();
    quiz_page.report_result([parseInt(result)], $.trim(extra));
  });

  var $tag_select = $('#select-tags');
  $tag_select.select2({
    placeholder: _("Select Tags"),
    allowClear: true
  });
  $tag_select.on('select2:select', function(name, event)
  {
    tag_page.render_bar(0);
    var tag = name.params.data.text;
    console.log(tag);
    $confirm_btn.button('loading');
    tag_page.render_bar(10, _('loading'));
    tag_page.load(
      tag,
      function(){ tag_page.render_bar(20, _('inserting')); },
      function(jqXHR, textStatus, errorThrown)
      {
        tag_page.render_bar(undefined, '' + jqXHR.status + ': ' + errorThrown, true);
      },
      function(){ $confirm_btn.button('reset'); tag_page.render_bar(100); });
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