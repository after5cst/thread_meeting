#ifndef KEEP_H
#define KEEP_H
#include <atomic>
#include <deque>
#include <iostream>
#include <memory>
#include <pybind11/pybind11.h>
#include <string>

#include "take.h"

class Keep {
public:
  static void bind(pybind11::module &);
  Keep(std::string name_in, pybind11::object payload_in)
      : name(name_in), payload(payload_in) {}

  // Methods for Python access
  Take::pointer_t create_take();
  bool finished() const;
  int acknowledged() const;
  int protested() const;
  int pending() const;

  std::string name;
  pybind11::object payload;

private:
  std::deque<Take::status_t> m_deque;
};

#endif // KEEP_H
