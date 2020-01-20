#include "transcript_item.h"

#include "attendee.h"

#include "pybind11/chrono.h"
#include <sstream>

void TranscriptItem::bind(pybind11::module& m)
{
    pybind11::class_<TranscriptItem, TranscriptItem::pointer_t>(
                m, "TranscriptItem")
        .def(pybind11::init<std::string, TranscriptType>(),
             pybind11::arg("message") = "",
             pybind11::arg("message_type") = TranscriptType::custom)
        .def("__repr__",
            [](const TranscriptItem &a) {
                return "<thread_Meeting.TranscriptItem>";
            })
        .def_readonly("source", &TranscriptItem::source)
        .def_readonly("message", &TranscriptItem::message)
        .def_readonly("message_type", &TranscriptItem::message_type)
        .def_readonly("timestamp", &TranscriptItem::timestamp)
        ;
}

TranscriptItem::TranscriptItem(std::string message_in,
                                     TranscriptType transcript_type)
    : message(message_in),
      message_type(transcript_type),
      timestamp(pybind11::cast(std::chrono::system_clock::now()))
{
    if (message_in.size() == 0)
    {
        throw std::invalid_argument("Message may not be empty.");
    }

    source = verify_thread_name(std::string());
}