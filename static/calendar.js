$(document).ready(function() {
    $('#calendar').fullCalendar({
        header: {
            left: 'prev,next today',
            center: 'title',
            right: 'month,agendaWeek,agendaDay'
        },
        editable: true,
        droppable: true,
        events: [
            {% for event in all_events %}
            {
                title: '{{ event.title }}',
                start: '{{ event.date.strftime('%Y-%m-%d') }}',
                url: "{{ url_for('edit_event', event_id=event.id) }}"
            },
            {% endfor %}
        ],
        eventClick: function(event) {
            if (confirm("Voulez-vous modifier cet événement ?")) {
                window.location.href = event.url;
            }
            return false;
        }
    });
});
