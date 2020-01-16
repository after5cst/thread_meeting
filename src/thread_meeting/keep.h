#ifndef KEEP_H
#define KEEP_H
#include <atomic>
#include <iostream>
#include <map>
#include <memory>
#include <string>
#include <pybind11/pybind11.h>

#include "take.h"

class Keep
{
public:
    static void bind(pybind11::module&);
    Keep(std::string name_in, pybind11::object payload_in)
        : name(name_in), payload(payload_in) {}

    // Methods for Python access
    Take::pointer_t create_take(std::string take_name);
    bool finished() const;
    pybind11::list acknowledged() const;
    pybind11::list protested() const;
    pybind11::list pending() const;

    std::string name;
    pybind11::object payload;
private:
    std::map< std::string, Take::status_t > m_map;
};

#endif // KEEP_H
