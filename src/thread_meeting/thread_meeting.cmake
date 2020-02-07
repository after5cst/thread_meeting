# Set current directory for adding sources
set (HERE ${CMAKE_CURRENT_LIST_DIR})

target_sources("${PROJECT_NAME}"
    PRIVATE
    "${HERE}/attendee.cpp"
    "${HERE}/attendee.h"
    "${HERE}/attendee_scope.cpp"
    "${HERE}/attendee_scope.h"
    "${HERE}/baton.cpp"
    "${HERE}/baton.h"
    "${HERE}/baton_scope.cpp"
    "${HERE}/baton_scope.h"
    "${HERE}/enter_exit.cpp"
    "${HERE}/enter_exit.h"
    "${HERE}/functions.cpp"
    "${HERE}/functions.h"
    "${HERE}/globals.cpp"
    "${HERE}/globals.h"
    "${HERE}/interruptable_scope.cpp"
    "${HERE}/interruptable_scope.h"
    "${HERE}/keep.cpp"
    "${HERE}/keep.h"
    "${HERE}/priority_queue.cpp"
    "${HERE}/priority_queue.h"
    "${HERE}/take.cpp"
    "${HERE}/take.h"
    "${HERE}/transcript_item.cpp"
    "${HERE}/transcript_item.h"
    "${HERE}/transcript_scope.cpp"
    "${HERE}/transcript_scope.h"
    )
