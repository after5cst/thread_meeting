#ifndef ATTENDEE_H
#define ATTENDEE_H
#include <memory>
#include <pybind11/pybind11.h>

class Attendee : public std::enable_shared_from_this<Attendee>
{
public:
    typedef std::shared_ptr<Attendee> pointer_t;
    Attendee(std::string name_) : name(name_) {}
    static void bind(pybind11::module&);

    std::string name;
private:
};

#endif // ATTENDEE_H
