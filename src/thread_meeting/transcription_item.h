#ifndef _TRANSCIPTION_ITEM
#define _TRANSCIPTION_ITEM

#include "globals.h"
#include "pybind11/pybind11.h"

#include <memory>

class TranscriptionItem
{
public:
    typedef std::unique_ptr<TranscriptionItem> pointer_t;
    static void bind(pybind11::module& m);

    TranscriptionItem(std::string message_in,
                      TranscriptionType transcription_type);

    std::string source;
    std::string message;
    TranscriptionType message_type;
    pybind11::object timestamp;
private:
};

#endif // _TRANSCIPTION_ITEM
