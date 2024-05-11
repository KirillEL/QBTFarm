var chart = null;
var flags = [];
var skipped_or_rejected_flags = [];
var time = [];
var split_time = [];
var hours;
var minutes;
var seconds;
var arr = [];

function padLeft(s, length) {
    s = s.toString();
    while (s.length < length)
        s = '0' + s;
    return s;
}

function dateToString(date) {
    return padLeft(date.getFullYear(), 4) + '-' + padLeft(date.getMonth() + 1, 2) + '-' +
        padLeft(date.getDate(), 2) + ' ' +
        padLeft(date.getHours(), 2) + ':' + padLeft(date.getMinutes(), 2) + ':' +
        padLeft(date.getSeconds(), 2);
}

function escapeHtml(text) {
    return $('<div>').text(text).html();
}

function generateFlagTableRows(rows) {
    var html = '';
    rows.forEach(function (item) {
        var cells = [
            item.sploit,
            item.team !== null ? item.team : '',
            item.flag,
            dateToString(new Date(item.time * 1000)),
            item.status,
            item.checksystem_response !== null ? item.checksystem_response : ''
        ];

        if (item?.status === 'ACCEPTED') {
            html += '<tr style="box-shadow:inset 0px 0px 5px 5px rgba(0,200,0,0.5);">';
            cells.forEach(function (text) {
                html += '<td style="font-weight:700;font-size:10px;">' + escapeHtml(text) + '</td>';
            });
            html += '</tr>';
        } else if (item?.status === 'QUEUED') {
            html += '<tr style="box-shadow:inset 0px 0px 5px 5px rgba(0,0,0,0.5);">';
            cells.forEach(function (text) {
                html += '<td style="font-weight:700;font-size:10px;">' + escapeHtml(text) + '</td>';
            });
            html += '</tr>';
        } else {
            html += '<tr style="box-shadow:inset 0px 0px 5px 5px rgba(200,0,0,0.5);">';
            cells.forEach(function (text) {
                html += '<td style="font-weight:700;font-size:10px;">' + escapeHtml(text) + '</td>';
            });
            html += '</tr>';
        }

    });
    return html;
}


function generatePaginator(totalCount, rowsPerPage, pageNumber) {
    var totalPages = Math.ceil(totalCount / rowsPerPage);
    var firstShown = Math.max(1, pageNumber - 3);
    var lastShown = Math.min(totalPages, pageNumber + 3);

    var html = '';
    if (firstShown > 1)
        html += '<li class="page-item"><a class="page-link" href="#" data-content="1">«</a></li>';

    for (var i = firstShown; i <= lastShown; i++) {
        var extraClasses = (i === pageNumber ? "active" : "");
        html += '<li class="page-item ' + extraClasses + '">' +
            '<a class="page-link" href="#" data-content="' + i + '">' + i + '</a>' +
            '</li>';
    }

    if (lastShown < totalPages)
        html += '<li class="page-item">' +
            '<a class="page-link" href="#" data-content="' + totalPages + '">»</a>' +
            '</li>';
    return html;
}


function getPageNumber() {
    return parseInt($('#page-number').val());
}


function setPageNumber(number) {
    $('#page-number').val(number);
}


var queryInProgress = false;

function showFlags() {
    if (queryInProgress)
        return;
    queryInProgress = true;
    $('.search-results').hide();
    $('.query-status').html('Loading...').show();

    $.post('/ui/show_flags', $('#show-flags-form').serialize())
        .done(function (response) {
            $('.search-results tbody').html(generateFlagTableRows(response.rows));

            $('.search-results .total-count').text(response.total_count);
            $('.search-results .total-accepted-count').text(response.total_accepted_count);
            $('.search-results .total-skipped-count').text(response.total_skipped_count);
            $('.search-results .pagination').html(generatePaginator(
                response.total_count, response.rows_per_page, getPageNumber()));
            $('.search-results .page-link').click(function (event) {
                event.preventDefault();

                setPageNumber($(this).data("content"));
                showFlags();
            });

            $('.query-status').hide();
            $('.search-results').show();
        })
        .fail(function () {
            $('.query-status').html("Failed to load flags from the farm server");
        })
        .always(function () {
            queryInProgress = false;
        });


}


function postFlagsManual() {
    if (queryInProgress)
        return;
    queryInProgress = true;

    $.post('/ui/post_flags_manual', $('#post-flags-manual-form').serialize())
        .done(function () {
            var sploitSelect = $('#sploit-select');
            if ($('#sploit-manual-option').empty())
                sploitSelect.append($('<option id="sploit-manual-option">Manual</option>'));
            sploitSelect.val('Manual');

            $('#team-select, #flag-input, #time-since-input, #time-until-input, ' +
                '#status-select, #checksystem-response-input').val('');

            queryInProgress = false;
            showFlags();
        })
        .fail(function () {
            $('.query-status').html("Failed to post flags to the farm server");
            queryInProgress = false;
        });
}


function showGraphic() {
    $('.btn-show-graph').attr('disabled', true)

    $.get('/ui/get_info')
        .done(function (response) {
            split_time = [];
            time = [];
            time = response.time;
            for (let t in time) split_time.push(time[t].split(' ')[1])

            flags = response.flags;
            skipped_or_rejected_flags = response.skipped_or_rejected_flags;
            var ctx = document.getElementById('container-graph-canvas').getContext('2d');
            console.log(split_time);
            console.log(flags);
            chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: split_time,
                    datasets: [
                        {
                            label: 'Count Accepted flags',
                            data: flags,
                            backgroundColor: 'rgba(75,192,192,0.2)',
                            borderColor: 'rgba(75,192,192,1)',
                            borderWidth: 2,
                            pointBackgroundColor: 'rgba(75,192,192,1)',
                            pointBorderColor: 'rgba(75,192,192,1)',
                            tension: 0.4,
                            pointRadius: 5,
                        },
                        {
                            label: 'Count Skipped/Rejected flags',
                            data: skipped_or_rejected_flags,
                            backgroundColor: 'rgba(255, 99, 132, 0.2)',
                            borderColor: 'rgba(255, 99, 132, 1)',
                            borderWidth: 2,
                            pointBackgroundColor: 'rgba(255, 99, 132, 1)',
                            pointBorderColor: 'rgba(255, 99, 132, 1)',
                            tension: 0.4,
                            pointRadius: 5,
                        }
                    ]
                },
                options: {}
            }
            );
            chart.render();

        });
}


$(function () {

    showFlags();
    $('#show-flags-form').submit(function (event) {
        event.preventDefault();
        setPageNumber(1);
        showFlags();
        chart.destroy();
        $('.btn-show-graph').attr('disabled', false)
    });

    $('#post-flags-manual-form').submit(function (event) {
        event.preventDefault();
        postFlagsManual();
    });

    $('.btn-show-graph').click(() => {
        $('.search-results').css('display', 'none');
        setTimeout(() => {
            showGraphic();
        }, 250);
    });
});
