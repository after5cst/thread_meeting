#ifndef _TRANSCIPTION_ITEM
#define _TRANSCIPTION_ITEM

#include "globals.h"
#include "pybind11/pybind11.h"

#include <memory>

class TranscriptItem
{
public:
    typedef std::unique_ptr<TranscriptItem> pointer_t;
    static void bind(pybind11::module& m);

    TranscriptItem(std::string message_in,
                      TranscriptType transcript_type);

    std::string source;
    std::string message;
    TranscriptType message_type;
    pybind11::object timestamp;
private:
};

#endif // _TRANSCIPTION_ITEM
