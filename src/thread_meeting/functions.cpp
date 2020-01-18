#include "functions.h"
#include "attendee_scope.h"
#include "transcription_item.h"
#include "transcription_scope.h"
#include "globals.h"

std::unique_ptr< EnterExit > transcriber()
{
    return std::make_unique< TranscriptionScope >();
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
        if (auto ptr = iter->second.lock())
        {
            result = pybind11::cast(ptr);
        }
    }
    return result;
}


pybind11::object transcribe(std::string message,
                            TranscriptionType transcription_type)
{
    if (g_transcription)
    {
        auto item = pybind11::cast(
                    TranscriptionItem(message, transcription_type));
        g_transcription->append(item);
        return item;
    }
    return pybind11::none();
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

    pybind11::enum_<TranscriptionType>(m, "TranscriptionType", pybind11::arithmetic())
            .value("Ack", TranscriptionType::ack)
            .value("Custom", TranscriptionType::custom)
            .value("Enter", TranscriptionType::enter)
            .value("Exit", TranscriptionType::exit)
            .value("Nack", TranscriptionType::nack)
            .value("Recv", TranscriptionType::recv)
            .value("Send", TranscriptionType::send)
            .value("State", TranscriptionType::state)
            ;

    m.def("participate", &participate, pybind11::arg("attendee_name") = "");
    m.def("me", &me);
    m.def("transcribe", &transcribe,
          pybind11::arg("message"),
          pybind11::arg("transcription_type") = TranscriptionType::custom
          );
   m.def("transcriber", &transcriber);
}
