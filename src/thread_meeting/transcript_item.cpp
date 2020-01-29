#include "transcript_item.h"

#include "attendee.h"

#include <chrono>
#include <sstream>

void TranscriptItem::bind(pybind11::module &m) {
  pybind11::class_<TranscriptItem, TranscriptItem::pointer_t> o(
      m, "TranscriptItem", R"pbdoc(
An item for the meeting transcript.
)pbdoc");

  o.def(pybind11::init<std::string, TranscriptType>(),
        R"pbdoc(
Initialization function.

:param message: The text message for the transcript.
:param payload: The optional payload object.
)pbdoc",
        pybind11::arg("message") = "",
        pybind11::arg("ti_type") = TranscriptType::custom);

  o.def("__repr__", [](const TranscriptItem &a) {
    std::stringstream sstr;
    sstr << "< " << a.source << " --[" << a.message << ","
         << as_string(a.ti_type) << "]--> " << a.destination << " >";
    return sstr.str();
  });

  o.def_readonly("source", &TranscriptItem::source,
                 R"pbdoc(
The originator of the item.
This attribute is read-only.
)pbdoc");

  o.def_readonly("destination", &TranscriptItem::destination,
                 R"pbdoc(
The expected destination of the item, if any.
This attribute is read-only.
)pbdoc");

  o.def_readonly("message", &TranscriptItem::message,
                 R"pbdoc(
The message text.
This attribute is read-only.
)pbdoc");

  o.def_readonly("ti_type", &TranscriptItem::ti_type,
                 R"pbdoc(
The type of the item.  This will be an enumeration of TranscriptType.
This attribute is read-only.
)pbdoc");

  o.def_readonly("timestamp", &TranscriptItem::timestamp,
                 R"pbdoc(
The timestamp when the item was created.
This attribute is read-only.
)pbdoc");

  // fields to describe object.

  o.def_property_readonly_static(
      "oas_version", [](pybind11::object /* self */) { return 1.0; },
      R"pbdoc(
A version number for this structure.
If fields are added/removed/changed, the version number should change.
This attribute is a static member of the class.
)pbdoc");

  o.def_property_readonly_static(
      "oas_fields",
      [](pybind11::object /* self */) {
        pybind11::list fields;

        pybind11::dict timestamp_info;
        timestamp_info["name"] = "timestamp";
        timestamp_info["tt_dtype"] = "daystamp";
        timestamp_info["desc"] = "seconds since epoch";
        fields.append(timestamp_info);

        pybind11::dict source_info;
        source_info["name"] = "source";
        fields.append(source_info);

        pybind11::dict ti_type_info;
        ti_type_info["name"] = "ti_type";
        fields.append(ti_type_info);

        pybind11::dict message_info;
        message_info["name"] = "message";
        fields.append(message_info);

        pybind11::dict destination_info;
        destination_info["name"] = "destination";
        fields.append(destination_info);

        return pybind11::tuple(fields);
      },
      R"pbdoc(
A dictionary defining the fields and data types in the structure.
If this changes, oas_version should also change.
This attribute is a static member of the class.
)pbdoc");
}

TranscriptItem::TranscriptItem(std::string message_in,
                               TranscriptType transcript_type,
                               thread_id_t destination_id)
    : source(verify_thread_name(std::string())),
      destination(verify_thread_name(std::string(), destination_id)),
      message(message_in), ti_type(transcript_type), timestamp(0.0) {
  if (message_in.size() == 0) {
    throw std::invalid_argument("Message may not be empty.");
  }
  uint64_t now = std::chrono::duration_cast<std::chrono::milliseconds>(
                     std::chrono::system_clock::now().time_since_epoch())
                     .count();
  timestamp = now / 1000.0;
}
