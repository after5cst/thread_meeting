#include "functions.h"
#include "attendee_scope.h"
#include "transcript_item.h"
#include "transcript_scope.h"
#include "globals.h"

std::unique_ptr< EnterExit > transcriber()
{
    return std::make_unique< TranscriptScope >();
}

std::unique_ptr< EnterExit > participate(std::string attendee_name)
{
    return std::make_unique< AttendeeScope >(attendee_name);
}

pybind11::object me()
{
    pybind11::object result = pybind11::none();
    auto id = PyThread_get_thread_ident();
    auto iter = g_attendees.find(id);
    if (iter != g_attendees.end())
    {
        result = pybind11::cast(iter->second);
    }
    return result;
}


pybind11::object transcribe(std::string message,
                            TranscriptType transcript_type)
{
    if (0 == g_transcripts.size())
    {
        return pybind11::none();
    }
    auto item = pybind11::cast(TranscriptItem(message, transcript_type));

    for (auto& transcript : g_transcripts)
    {
        transcript.second->push(item);
    }
    return item;
}

void bind_functions(pybind11::module& m)
{
    pybind11::enum_<MessageStatus>(m, "TakeStatus", pybind11::arithmetic())
            .value("Pending", MessageStatus::pending)
            .value("Acknowledged", MessageStatus::acknowledged)
            .value("Protested", MessageStatus::protested)
            ;

    pybind11::enum_<ThreadState>(m, "ThreadState", pybind11::arithmetic())
            .value("Unknown", ThreadState::unknown)
            .value("Idle", ThreadState::idle)
            .value("Working", ThreadState::working)
            .value("Busy", ThreadState::busy)
            .value("Presenter", ThreadState::presenter)
            ;

    pybind11::enum_<TranscriptType>(m, "TranscriptType", pybind11::arithmetic())
            .value("Ack", TranscriptType::ack)
            .value("Custom", TranscriptType::custom)
            .value("Enter", TranscriptType::enter)
            .value("Exit", TranscriptType::exit)
            .value("Nack", TranscriptType::nack)
            .value("Recv", TranscriptType::recv)
            .value("Send", TranscriptType::send)
            .value("State", TranscriptType::state)
            ;

    m.def("participate", &participate, pybind11::arg("attendee_name") = "");
    m.def("me", &me);
    m.def("transcribe", &transcribe,
          pybind11::arg("message"),
          pybind11::arg("transcript_type") = TranscriptType::custom
          );
   m.def("transcriber", &transcriber);
}
